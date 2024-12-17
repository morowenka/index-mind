// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "IndexMindApp",
    defaultLocalization: "ru",
    platforms: [
        .macOS(.v10_15)
    ],
    targets: [
        .executableTarget(
            name: "IndexMindApp",
            path: "Sources" // Удаляем 'resources', если они не используются
        )
    ]
)

