//
//  LinkTableCellView.swift
//  IndexMindApp
//
//  Created by Басов Марк Игоревич on 22.10.2024.
//

import Cocoa

class LinkTableCellView: NSTableCellView {
    @IBOutlet weak var linkTextField: NSTextField!

    override func awakeFromNib() {
        super.awakeFromNib()
        let gesture = NSClickGestureRecognizer(target: self, action: #selector(openFile))
        linkTextField.addGestureRecognizer(gesture)
        linkTextField.isEditable = false
    }

    @objc func openFile() {
        if let filePath = linkTextField?.stringValue {
            NSWorkspace.shared.openFile(filePath)
        }
    }
}
