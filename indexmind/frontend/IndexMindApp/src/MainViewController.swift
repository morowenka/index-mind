import Foundation
import Cocoa

// MARK: - Models for Requests and Progress Updates
struct AddDocumentsRequest: Codable {
    let file_paths: [String]
}

struct UpdateIndexesRequest: Codable {
    // Если нужны дополнительные параметры, добавьте их здесь
}

struct ProgressUpdate: Codable {
    let total_files: Int?
    let processed_file: String?
    let current_progress: Int?
    let indexing_complete: Bool?
    let indexer: String?
    let status: String?
    let error: String?
    let trace: String?
    let update_indexes_complete: Bool? // Добавлено для обработки завершения обновления индексов
}

struct SearchRequest: Codable {
    let query: String
    let n: Int?
    let filters: [String: String]?
}

struct DocumentMetadata: Codable {
    let creation_time: Int?
    let modification_time: Int?
    let file_hash: String?
    let file_path: String?
    let status: String?
}

struct RetrievedDocument: Codable {
    let id: String?
    let content: String?
    let metadata: DocumentMetadata?
    let score: Double?
}

struct SearchResponse: Codable {
    let response: String
    let retrieved_documents: [RetrievedDocument]?
}


class MainViewController: NSViewController, NSSearchFieldDelegate {
    @IBOutlet weak var progressIndicator: NSProgressIndicator!
    @IBOutlet weak var chatScrollView: NSScrollView!
    @IBOutlet weak var chatTextView: NSTextView!
    @IBOutlet weak var searchField: NSSearchField!
    @IBOutlet weak var deleteAllIndexes: NSButton!
    @IBOutlet weak var currentFileLabel: NSTextField!
    @IBOutlet weak var metadataScrollView: NSScrollView!

    var metadataStackView: NSStackView!
    var webSocketTask: URLSessionWebSocketTask?
    let urlSession = URLSession(configuration: .default)

    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Установка WebSocket-соединения
        setupWebSocket()
        
        // Configure chat text view to be read-only and scrollable
        chatTextView.isEditable = false
        chatScrollView.hasVerticalScroller = true
        
        // Initially hide currentFileLabel
        currentFileLabel.isHidden = true
        
        searchField.delegate = self
        
        metadataStackView.translatesAutoresizingMaskIntoConstraints = false
        metadataStackView.orientation = .vertical
        metadataStackView.spacing = 10
        metadataStackView.alignment = .leading
        
        self.metadataScrollView.hasVerticalScroller = true
        self.metadataScrollView.hasHorizontalScroller = false
        if let documentContentView = self.metadataStackView {
               self.metadataScrollView.documentView = documentContentView
          }
    }
    
    func displayMetadata(_ documents: [RetrievedDocument]) {
        DispatchQueue.main.async {
            // Очистка старых элементов из stack view
            self.metadataStackView.arrangedSubviews.forEach { subview in
                self.metadataStackView.removeArrangedSubview(subview)
                subview.removeFromSuperview()
            }
            // Создание блоков для каждого документа и добавление их в stack view
            for document in documents {
                print("Processing document: \(String(describing: document.id))")
                // Создание блока
                let box = NSBox()
                box.title = ""
                box.translatesAutoresizingMaskIntoConstraints = false
                box.isTransparent = true
                box.contentViewMargins = NSSize(width: 10, height: 10)
                box.wantsLayer = true
                box.layer?.cornerRadius = 8
                box.layer?.borderWidth = 1
                box.layer?.borderColor = NSColor.separatorColor.cgColor
                // Вложенный vertical stack view для содержимого блока
                let contentStack = NSStackView()
                contentStack.orientation = .vertical
                contentStack.spacing = 8
                contentStack.edgeInsets = NSEdgeInsets(top: 8, left: 8, bottom: 8, right: 8)
                contentStack.translatesAutoresizingMaskIntoConstraints = false
                box.contentView?.addSubview(contentStack)
                // Добавляем блок в stack view до установки ограничений
                self.metadataStackView.addArrangedSubview(box)
                // Устанавливаем размеры contentStack в box
                NSLayoutConstraint.activate([
                    contentStack.leadingAnchor.constraint(equalTo: box.leadingAnchor),
                    contentStack.trailingAnchor.constraint(equalTo: box.trailingAnchor),
                    contentStack.topAnchor.constraint(equalTo: box.topAnchor),
                    contentStack.bottomAnchor.constraint(equalTo: box.bottomAnchor),
                ])
                // Кнопка-ссылка для имени файла
                if let filePath = document.metadata?.file_path {
                    let fileButton = NSButton(title: (filePath as NSString).lastPathComponent,
                                              target: self,
                                              action: #selector(self.openFileInFinder(_:)))
                    fileButton.identifier = NSUserInterfaceItemIdentifier(filePath) // Указываем путь как идентификатор
                    fileButton.isBordered = false
                    fileButton.wantsLayer = true
                    fileButton.layer?.backgroundColor = NSColor.clear.cgColor
                    fileButton.font = NSFont.boldSystemFont(ofSize: 12)
                    fileButton.contentTintColor = NSColor.linkColor
                    contentStack.addArrangedSubview(fileButton)
                }
                // Время создания
                if let creationTime = document.metadata?.creation_time {
                    let creationTimeString = self.formatDate(timestamp: creationTime)
                    let creationTimeLabel = NSTextField(labelWithString: "Creation Time: \(creationTimeString)")
                    creationTimeLabel.font = NSFont.systemFont(ofSize: 12)
                    creationTimeLabel.textColor = NSColor.secondaryLabelColor
                    contentStack.addArrangedSubview(creationTimeLabel)
                }
                // Время модификации
                if let modificationTime = document.metadata?.modification_time {
                    let modificationTimeString = self.formatDate(timestamp: modificationTime)
                    let modificationTimeLabel = NSTextField(labelWithString: "Modification Time: \(modificationTimeString)")
                    modificationTimeLabel.font = NSFont.systemFont(ofSize: 12)
                    modificationTimeLabel.textColor = NSColor.secondaryLabelColor
                    contentStack.addArrangedSubview(modificationTimeLabel)
                }
                // Превью содержимого
                if let content = document.content {
                    let previewLabel = NSTextField(labelWithString: "Preview: \(content.prefix(50))...")
                    previewLabel.font = NSFont.systemFont(ofSize: 12)
                    previewLabel.textColor = NSColor.secondaryLabelColor
                    contentStack.addArrangedSubview(previewLabel)
                }
                // Оценка (score)
                if let score = document.score {
                    let scoreLabel = NSTextField(labelWithString: "Score: \(String(format: "%.2f", score))")
                    scoreLabel.font = NSFont.systemFont(ofSize: 12)
                    scoreLabel.textColor = NSColor.tertiaryLabelColor
                    contentStack.addArrangedSubview(scoreLabel)
                }
                // Устанавливаем размеры box в metadataStackView
                NSLayoutConstraint.activate([
                    box.widthAnchor.constraint(equalTo: self.metadataStackView.widthAnchor),
                    box.heightAnchor.constraint(equalToConstant: 150) // Фиксированная высота
                ])
            }
        }
    }

    /// Форматирует метку времени, удаляя +0000
    @objc func formatDate(timestamp: Int) -> String {
        let date = Date(timeIntervalSince1970: TimeInterval(timestamp))
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .short
        return dateFormatter.string(from: date)
    }
    
    @objc func openFileInFinder(_ sender: NSButton) {
        guard let filePath = sender.identifier?.rawValue else { return }
        let url = URL(fileURLWithPath: filePath)
        NSWorkspace.shared.activateFileViewerSelecting([url])
    }
    
    // MARK: - WebSocket Setup
    func setupWebSocket() {
        guard let url = URL(string: "ws://127.0.0.1:8000/ws/progress") else {
            showAlert(message: "Invalid WebSocket URL.")
            return
        }
        
        webSocketTask = urlSession.webSocketTask(with: url)
        webSocketTask?.resume()
        receiveWebSocketMessages()
    }

    func receiveWebSocketMessages() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .failure(let error):
                print("❌ WebSocket Receive Error: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self?.showAlert(message: "WebSocket Error: \(error.localizedDescription)")
                }
            case .success(let message):
                switch message {
                case .string(let text):
                    print("📥 WebSocket Received Text: \(text)")
                    self?.processWebSocketText(text)
                case .data(let data):
                    print("📥 WebSocket Received Data: \(data)")
                    self?.processWebSocketData(data)
                @unknown default:
                    print("Received an unknown message type")
                }
                
                // Continue receiving messages
                self?.receiveWebSocketMessages()
            }
        }
    }

    private func processWebSocketText(_ text: String) {
        print("📊 Processing WebSocket Text: \(text)")
        let lines = text.components(separatedBy: "\n").filter { !$0.isEmpty }
        for line in lines {
            if let data = line.data(using: .utf8),
               let progressUpdate = try? JSONDecoder().decode(ProgressUpdate.self, from: data) {
                handleProgressUpdate(progressUpdate)
            } else {
                print("❌ Failed to decode progress update from text: \(line)")
            }
        }
    }

    private func processWebSocketData(_ data: Data) {
        print("📊 Processing WebSocket Data")
        if let progressUpdate = try? JSONDecoder().decode(ProgressUpdate.self, from: data) {
            handleProgressUpdate(progressUpdate)
        } else {
            print("❌ Failed to decode binary progress update")
        }
    }

    // MARK: - Search Action
    func controlTextDidEndEditing(_ obj: Notification) {
        guard let searchField = obj.object as? NSSearchField else { return }

        let query = searchField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if query.isEmpty {
            showAlert(message: "Пожалуйста, введите запрос для поиска.")
            return
        }

        // Очищаем строку поиска только один раз
        searchField.stringValue = ""
        
        self.view.window?.makeFirstResponder(chatTextView)
        
        // Отправляем запрос
        let searchRequest = SearchRequest(query: query, n: 5, filters: nil)
        
        performSearch(request: searchRequest)
        
    }
    
    func performSearch(request: SearchRequest) {
        guard let url = URL(string: "http://127.0.0.1:8000/search") else {
            showAlert(message: "Invalid backend URL.")
            return
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            let jsonData = try JSONEncoder().encode(request)
            urlRequest.httpBody = jsonData
            
            print("🌐 Sending Search Request: \(String(data: jsonData, encoding: .utf8) ?? "")")
            
            let task = URLSession.shared.dataTask(with: urlRequest) { [weak self] data, response, error in
                if let error = error {
                    print("❌ Search Request Error: \(error.localizedDescription)")
                    DispatchQueue.main.async {
                        self?.showAlert(message: "Search Error: \(error.localizedDescription)")
                    }
                    return
                }

                guard let data = data else {
                    print("❌ No data received")
                    return
                }

                // Print raw response for debugging
                if let rawResponse = String(data: data, encoding: .utf8) {
                    print("📬 Raw Search Response: \(rawResponse)")
                }

                do {
                    let searchResponse = try JSONDecoder().decode(SearchResponse.self, from: data)
                    print("📬 Decoded Search Response: \(searchResponse)")
                    
                    DispatchQueue.main.async { [weak self] in
                        guard let self = self else { return }
                        self.updateChatView(userQuery: request.query,
                                            machineResponse: searchResponse.response)
                        
                        // Новый вызов для отображения метаданных
                        if let retrievedDocuments = searchResponse.retrieved_documents {
                            self.displayMetadata(retrievedDocuments)
                        }
                    }
                } catch {
                    print("❌ Decoding Error: \(error)")
                    DispatchQueue.main.async {
                        self?.showAlert(message: "Error decoding search response: \(error)")
                    }
                }
            }
            task.resume()
        } catch {
            print("❌ JSON Encoding Error: \(error)")
            showAlert(message: "Error preparing search request: \(error.localizedDescription)")
        }
    }

    func updateChatView(userQuery: String, machineResponse: String) {
        let attributedText = NSMutableAttributedString()

        let userStyle: [NSAttributedString.Key: Any] = [
            .foregroundColor: NSColor.systemBlue,
            .font: NSFont.boldSystemFont(ofSize: 14)
        ]

        let machineStyle: [NSAttributedString.Key: Any] = [
            .foregroundColor: NSColor.systemGreen,
            .font: NSFont.systemFont(ofSize: 14)
        ]

        attributedText.append(NSAttributedString(string: "👤 \(userQuery)\n", attributes: userStyle))

        let currentAttributedText = chatTextView.textStorage
        currentAttributedText?.append(attributedText) // Добавляем запрос пользователя сразу

        chatTextView.scrollRangeToVisible(NSRange(location: attributedText.length, length: 0))

        // Анимация для появления ответа машины
        let machineResponseString = "🤖 \(machineResponse)\n\n"
        var currentIndex = 0

        Timer.scheduledTimer(withTimeInterval: 0.005, repeats: true) { timer in
            guard currentIndex < machineResponseString.count else {
                timer.invalidate()
                return
            }

            let index = machineResponseString.index(machineResponseString.startIndex, offsetBy: currentIndex)
            let char = String(machineResponseString[index])

            let charAttributes = [
                NSAttributedString.Key.foregroundColor: NSColor.systemGreen,
                NSAttributedString.Key.font: NSFont.systemFont(ofSize: 14)
            ]

            let attributedChar = NSAttributedString(string: char, attributes: charAttributes)
            currentAttributedText?.append(attributedChar)

            let range = NSRange(location: currentAttributedText?.length ?? 0, length: 0)
            self.chatTextView.scrollRangeToVisible(range)

            currentIndex += 1
        }
    }


    // MARK: - Add Folder Action
    @IBAction func addFolderButtonClicked(_ sender: Any) {
        let dialog = NSOpenPanel()
        dialog.title = "Выберите папки для индексации"
        dialog.canChooseFiles = false
        dialog.canChooseDirectories = true
        dialog.allowsMultipleSelection = true
        
        if dialog.runModal() == .OK {
            let selectedFolders = dialog.urls.map { $0.path }
            sendFoldersToBackend(selectedFolders)
        }
    }

    // MARK: - Refresh Indexes Action
    @IBAction func refreshIndicesButtonClicked(_ sender: Any) {
        sendUpdateIndexesRequest()
    }
    
    // MARK: - Backend Request Methods
    
    /// Отправка выбранных папок на бэкэнд для индексации
    // MARK: - Remove Start Alert and Reset Progress Bar in sendFoldersToBackend
    func sendFoldersToBackend(_ folders: [String]) {
        guard !folders.isEmpty else {
            showAlert(message: "Не выбрано ни одной папки для индексации.")
            return
        }
        
        guard let url = URL(string: "http://127.0.0.1:8000/add_indexes") else {
            showAlert(message: "Ошибка: Неверный URL бэкэнда.")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        let addRequest = AddDocumentsRequest(file_paths: folders)
        do {
            let bodyData = try JSONEncoder().encode(addRequest)
            request.httpBody = bodyData
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        } catch {
            showAlert(message: "Ошибка при кодировании данных запроса.")
            return
        }

        // Reset the progress bar and start animation without showing an alert
        DispatchQueue.main.async {
            self.progressIndicator.doubleValue = 0
            self.currentFileLabel.stringValue = "Начало индексации..."
            self.progressIndicator.isIndeterminate = false
            self.progressIndicator.startAnimation(self)
        }
        
        // Send request in the background
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.showAlert(message: "Ошибка при добавлении индексов: \(error.localizedDescription)")
                    self?.progressIndicator.stopAnimation(self)
                    self?.progressIndicator.isIndeterminate = false
                    return
                }
                
                // Stop indeterminate mode and start updating based on progress updates
                self?.progressIndicator.isIndeterminate = false
            }
        }
        task.resume()
    }

    /// Отправка запроса на обновление индексов
    func sendUpdateIndexesRequest() {
        guard let url = URL(string: "http://127.0.0.1:8000/update_indexes") else {
            showAlert(message: "Ошибка: Неверный URL бэкэнда.")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        let updateRequest = UpdateIndexesRequest()
        do {
            let bodyData = try JSONEncoder().encode(updateRequest)
            request.httpBody = bodyData
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        } catch {
            showAlert(message: "Ошибка при кодировании данных запроса.")
            return
        }

        // Запускаем индикатор прогресса
        DispatchQueue.main.async {
            self.progressIndicator.doubleValue = 0
            self.currentFileLabel.stringValue = "Начало обновления индексов..."
            self.progressIndicator.isIndeterminate = false
            self.progressIndicator.startAnimation(self)
        }
        
        // Отправляем запрос в фоне
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.showAlert(message: "Ошибка при обновлении индексов: \(error.localizedDescription)")
                    self?.progressIndicator.stopAnimation(self)
                    self?.progressIndicator.isIndeterminate = false
                    return
                }
                
                // Предполагается, что сервер сразу возвращает "Index updating started"
                self?.progressIndicator.isIndeterminate = false
            }
        }
        task.resume()
    }
    
    // MARK: - Progress Handling
    func handleProgressUpdate(_ update: ProgressUpdate) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // Show/hide currentFileLabel only during indexing
            self.currentFileLabel.isHidden = false
            
            // Rest of the existing handleProgressUpdate logic remains the same
            if let total = update.total_files {
                self.progressIndicator.minValue = 0
                self.progressIndicator.maxValue = Double(total)
                self.progressIndicator.doubleValue = 0
                self.progressIndicator.isIndeterminate = false
            }

            if let processedFile = update.processed_file {
                self.currentFileLabel.stringValue = "Processing: \(URL(fileURLWithPath: processedFile).lastPathComponent)"
            }

            if let processed = update.current_progress, let total = update.total_files {
                self.progressIndicator.doubleValue = Double(processed)
            }

            if let indexingComplete = update.indexing_complete, indexingComplete {
                self.progressIndicator.doubleValue = self.progressIndicator.maxValue
                self.progressIndicator.stopAnimation(self)
                self.currentFileLabel.stringValue = "Indexing Complete"
                self.currentFileLabel.isHidden = true
                self.showAlert(message: "Indexing successfully completed.")
            }

            if let updateComplete = update.update_indexes_complete, updateComplete {
                self.progressIndicator.doubleValue = self.progressIndicator.maxValue
                self.progressIndicator.stopAnimation(self)
                self.currentFileLabel.stringValue = "Indexes Update Complete"
                self.currentFileLabel.isHidden = true
                self.showAlert(message: "Indexes update successfully completed.")
            }

            if let error = update.error {
                self.currentFileLabel.stringValue = "Error: \(error)"
                self.showAlert(message: "Error: \(error)")
                if let trace = update.trace {
                    print("Trace: \(trace)")
                }
                self.progressIndicator.stopAnimation(self)
                self.currentFileLabel.isHidden = true
            }
        }
    }

    @IBAction func deleteAllIndexesButtonClicked(_ sender: Any) {
        guard let url = URL(string: "http://127.0.0.1:8000/delete_all_documents") else {
            showAlert(message: "Ошибка: Неверный URL бэкэнда.")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.showAlert(message: "Ошибка при удалении документов: \(error.localizedDescription)")
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    self?.showAlert(message: "Все документы успешно удалены.")
                } else {
                    self?.showAlert(message: "Не удалось удалить документы.")
                }
            }
        }
        task.resume()
    }

    // MARK: - Utility Functions
    func showAlert(message: String) {
        DispatchQueue.main.async {
            let alert = NSAlert()
            alert.messageText = message
            alert.addButton(withTitle: "OK")
            alert.runModal()
        }
    }

    override func viewDidAppear() {
        super.viewDidAppear()
        
        // Add additional error tracking
        NotificationCenter.default.addObserver(self, selector: #selector(handleTerminationError), name: NSNotification.Name("NSErrorNotification"), object: nil)
    }

    @objc func handleTerminationError(_ notification: Notification) {
        if let error = notification.userInfo?["error"] as? Error {
            print("Received termination error: \(error.localizedDescription)")
            showAlert(message: "Системная ошибка: \(error.localizedDescription)")
        }
    }
    
    deinit {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        NotificationCenter.default.removeObserver(self)
    }
}
