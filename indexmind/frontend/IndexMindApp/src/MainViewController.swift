//
//  MainViewController.swift
//  IndexMindApp
//
//  Created by Басов Марк Игоревич on 22.10.2024.
//

import Foundation
import Cocoa

struct SearchResult: Decodable {
    let content: String?
    let imageData: Data?
    let filePath: String
}

class MainViewController: NSViewController, NSTableViewDelegate, NSTableViewDataSource {
    @IBOutlet weak var progressIndicator: NSProgressIndicator!
    @IBOutlet weak var chatScrollView: NSScrollView!
    @IBOutlet weak var chatTextView: NSTextView!
    @IBOutlet weak var searchField: NSSearchField!
    @IBOutlet weak var resultsScrollView: NSScrollView!
    @IBOutlet weak var resultsTableView: NSTableView!
    
    var searchResults: [SearchResult] = []
    var foldersToIndex: [String] = []
    
    @IBAction func addFolderButtonClicked(_ sender: Any) {
        let dialog = NSOpenPanel()
        dialog.title = "Выберите папки для индексации"
        dialog.canChooseFiles = false
        dialog.canChooseDirectories = true
        dialog.allowsMultipleSelection = true
        if dialog.runModal() == .OK {
            for result in dialog.urls {
                let folderPath = result.path
                if !foldersToIndex.contains(folderPath) {
                    foldersToIndex.append(folderPath)
                    showAlert(message: "Папка добавлена: \(folderPath)")
                } else {
                    showAlert(message: "Папка уже добавлена: \(folderPath)")
                }
            }
            saveFoldersList()
        }

    }
    
    @IBAction func refreshIndicesButtonClicked(_ sender: Any) {
        if foldersToIndex.isEmpty {
            showAlert(message: "Сначала добавьте хотя бы одну папку для индексации.")
            return
        }
        progressIndicator.startAnimation(self)
        DispatchQueue.global(qos: .background).async {
            self.runIndexingForFolders()
        }
    }

    func runIndexingForFolders() {
        let success = runIndexingScript(folderPaths: foldersToIndex)
        DispatchQueue.main.async {
            if success {
                self.showAlert(message: "Индексация успешно завершена.")
            } else {
                self.showAlert(message: "Ошибка индексации.")
            }
            self.progressIndicator.stopAnimation(self)
        }
    }

    func runIndexingScript(folderPaths: [String]) -> Bool {
        let process = Process()
        process.launchPath = "/usr/bin/env"
        var arguments = ["python3", "../backend/src/index_documents.py"]
        arguments.append(contentsOf: folderPaths)
        process.arguments = arguments

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        process.launch()
        process.waitUntilExit()

        let status = process.terminationStatus

        return status == 0
    }

    func showAlert(message: String) {
        DispatchQueue.main.async {
            let alert = NSAlert()
            alert.messageText = message
            alert.addButton(withTitle: "OK")
            alert.runModal()
        }
    }
    
    func saveFoldersList() {
        UserDefaults.standard.set(foldersToIndex, forKey: "FoldersToIndex")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        resultsTableView.delegate = self
        resultsTableView.dataSource = self
        
        // Загрузка списка папок
        if let savedFolders = UserDefaults.standard.stringArray(forKey: "FoldersToIndex") {
            foldersToIndex = savedFolders
        }
    }
    
    // MARK: - Search Functionality

    @IBAction func searchFieldAction(_ sender: NSSearchField) {
        let query = searchField.stringValue
        if query.isEmpty {
            return
        }
        performSearch(query: query)
    }
    
    func performSearch(query: String) {
        let process = Process()
        process.launchPath = "/usr/bin/env"
        process.arguments = ["python3", "../backend/src/search_documents.py", query]
        
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        
        process.launch()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8) {
            parseSearchResults(jsonString: output)
        }
    }
    
    func parseSearchResults(jsonString: String) {
        let data = jsonString.data(using: .utf8)!
        do {
            let results = try JSONDecoder().decode([SearchResult].self, from: data)
            self.searchResults = results
            resultsTableView.reloadData()
        } catch {
            print("Ошибка при разборе результатов поиска: \(error)")
        }
    }
    
    // MARK: - NSTableViewDataSource Methods

    func numberOfRows(in tableView: NSTableView) -> Int {
        return searchResults.count
    }

    // MARK: - NSTableViewDelegate Methods

    func tableView(_ tableView: NSTableView, viewFor tableColumn: NSTableColumn?, row: Int) -> NSView? {
        let result = searchResults[row]
        
        if tableColumn?.identifier.rawValue == "ContentColumn" {
            if let cell = tableView.makeView(withIdentifier: NSUserInterfaceItemIdentifier("ContentCell"), owner: self) as? ContentTableCellView {
                if let imageData = result.imageData {
                    cell.contentImageView.isHidden = false
                    cell.contentImageView.image = NSImage(data: imageData)
                    cell.contentTextField.isHidden = true
                } else if let contentText = result.content {
                    cell.contentImageView.isHidden = true
                    cell.contentTextField.isHidden = false
                    cell.contentTextField.stringValue = contentText
                }
                return cell
            }
        } else if tableColumn?.identifier.rawValue == "LinkColumn" {
            if let cell = tableView.makeView(withIdentifier: NSUserInterfaceItemIdentifier("LinkCell"), owner: self) as? LinkTableCellView {
                cell.linkTextField.stringValue = result.filePath
                return cell
            }
        }
        return nil
    }
}

