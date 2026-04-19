#!/usr/bin/env swift

import Foundation
import PDFKit

struct ExcerptSpec {
    let title: String
    let anchor: String
}

struct DocumentSpec {
    let pdfPath: String
    let outputStem: String
    let excerpts: [ExcerptSpec]
}

enum SnapshotError: Error, CustomStringConvertible {
    case invalidArguments(String)
    case unreadablePDF(String)
    case missingAnchor(document: String, anchor: String)

    var description: String {
        switch self {
        case let .invalidArguments(message):
            return message
        case let .unreadablePDF(path):
            return "Unable to open PDF at \(path)"
        case let .missingAnchor(document, anchor):
            return "Anchor not found in \(document): \(anchor)"
        }
    }
}

func parseArguments() throws -> (projectRoot: String, outputDir: String) {
    var projectRoot = FileManager.default.currentDirectoryPath
    var outputDir = "dist/pdf_text_snapshots"

    var index = 1
    while index < CommandLine.arguments.count {
        let arg = CommandLine.arguments[index]
        switch arg {
        case "--project-root":
            index += 1
            guard index < CommandLine.arguments.count else {
                throw SnapshotError.invalidArguments("Missing value for --project-root")
            }
            projectRoot = CommandLine.arguments[index]
        case "--output-dir":
            index += 1
            guard index < CommandLine.arguments.count else {
                throw SnapshotError.invalidArguments("Missing value for --output-dir")
            }
            outputDir = CommandLine.arguments[index]
        case "--help":
            throw SnapshotError.invalidArguments(
                """
                Usage: swift scripts/export_pdf_text_snapshots.swift [--project-root PATH] [--output-dir PATH]
                """
            )
        default:
            throw SnapshotError.invalidArguments("Unknown argument: \(arg)")
        }
        index += 1
    }

    return (projectRoot, outputDir)
}

func normalizedLines(_ text: String) -> [String] {
    text
        .components(separatedBy: .newlines)
        .map { $0.trimmingCharacters(in: .whitespaces) }
        .filter { !$0.isEmpty }
}

func pageSnippet(pageText: String, anchor: String, contextLines: Int = 3) -> String {
    let lines = normalizedLines(pageText)
    guard let anchorIndex = lines.firstIndex(where: { $0.contains(anchor) }) else {
        return lines.prefix(12).joined(separator: "\n")
    }

    let lowerBound = max(0, anchorIndex - contextLines)
    let upperBound = min(lines.count, anchorIndex + contextLines + 1)
    return lines[lowerBound..<upperBound].joined(separator: "\n")
}

func joinedFullText(from pageTexts: [String]) -> String {
    pageTexts.enumerated().map { index, pageText in
        "=== Page \(index + 1) ===\n\(pageText.trimmingCharacters(in: .whitespacesAndNewlines))"
    }.joined(separator: "\n\n")
}

func extractDocument(
    spec: DocumentSpec,
    projectRoot: String,
    outputDir: URL
) throws -> [String] {
    let pdfURL = URL(fileURLWithPath: projectRoot).appendingPathComponent(spec.pdfPath)
    guard let document = PDFDocument(url: pdfURL) else {
        throw SnapshotError.unreadablePDF(pdfURL.path)
    }

    var pageTexts: [String] = []
    pageTexts.reserveCapacity(document.pageCount)

    for pageIndex in 0..<document.pageCount {
        let text = document.page(at: pageIndex)?.string ?? ""
        pageTexts.append(text)
    }

    let fullText = joinedFullText(from: pageTexts)
    let fullTextURL = outputDir.appendingPathComponent("\(spec.outputStem).full.txt")
    try fullText.write(to: fullTextURL, atomically: true, encoding: .utf8)

    var excerptMarkdown: [String] = []
    excerptMarkdown.append("# \(spec.outputStem) Key Excerpts")
    excerptMarkdown.append("")
    excerptMarkdown.append("Source PDF: `\(spec.pdfPath)`")
    excerptMarkdown.append("")

    for excerpt in spec.excerpts {
        guard let pageIndex = pageTexts.firstIndex(where: { $0.contains(excerpt.anchor) }) else {
            throw SnapshotError.missingAnchor(document: spec.outputStem, anchor: excerpt.anchor)
        }
        let snippet = pageSnippet(pageText: pageTexts[pageIndex], anchor: excerpt.anchor)
        excerptMarkdown.append("## \(excerpt.title)")
        excerptMarkdown.append("")
        excerptMarkdown.append("- Page: \(pageIndex + 1)")
        excerptMarkdown.append("- Anchor: `\(excerpt.anchor)`")
        excerptMarkdown.append("")
        excerptMarkdown.append("```text")
        excerptMarkdown.append(snippet)
        excerptMarkdown.append("```")
        excerptMarkdown.append("")
    }

    let excerptURL = outputDir.appendingPathComponent("\(spec.outputStem).key_excerpts.md")
    try excerptMarkdown.joined(separator: "\n").write(to: excerptURL, atomically: true, encoding: .utf8)

    return [
        fullTextURL.lastPathComponent,
        excerptURL.lastPathComponent,
    ]
}

do {
    let arguments = try parseArguments()
    let outputDirURL = URL(fileURLWithPath: arguments.outputDir, relativeTo: URL(fileURLWithPath: arguments.projectRoot))
        .standardizedFileURL
    try FileManager.default.createDirectory(at: outputDirURL, withIntermediateDirectories: true)

    let documents = [
        DocumentSpec(
            pdfPath: "latex/ethical_riemann_hypothesis_en.pdf",
            outputStem: "ethical_riemann_hypothesis_en",
            excerpts: [
                ExcerptSpec(title: "Abstract Pi/B Excerpt", anchor: "introduce Π(x), the counting function for ethical primes"),
                ExcerptSpec(title: "Motivation Citation Excerpt", anchor: "these systems fail [Jobin et al.,"),
                ExcerptSpec(title: "Figure 1 Caption Excerpt", anchor: "Dynamically generated quantum circuit")
            ]
        ),
        DocumentSpec(
            pdfPath: "latex/ethical_riemann_hypothesis_zh.pdf",
            outputStem: "ethical_riemann_hypothesis_zh",
            excerpts: [
                ExcerptSpec(title: "Abstract Pi/B Excerpt", anchor: "並引入Π(x) 作為複雜度級別100 以下的倫理質數計數函數。透過建立類似於對數"),
                ExcerptSpec(title: "Motivation Citation Excerpt", anchor: "如何失敗[Jobin et al.,"),
                ExcerptSpec(title: "Figure 1 Caption Excerpt", anchor: "動態產生的量子電路")
            ]
        ),
    ]

    var generatedFiles: [String] = []
    for document in documents {
        generatedFiles.append(contentsOf: try extractDocument(spec: document, projectRoot: arguments.projectRoot, outputDir: outputDirURL))
    }

    let indexURL = outputDirURL.appendingPathComponent("README.md")
    let indexText = """
    # PDF Text Snapshots

    Generated from the latest thesis PDFs using macOS `PDFKit` text extraction.

    Files:
    \(generatedFiles.sorted().map { "- `\($0)`" }.joined(separator: "\n"))
    """
    try indexText.write(to: indexURL, atomically: true, encoding: .utf8)

    print("Wrote PDF text snapshots to \(outputDirURL.path)")
    for file in generatedFiles.sorted() {
        print("- \(file)")
    }
    print("- \(indexURL.lastPathComponent)")
} catch {
    fputs("ERROR: \(error)\n", stderr)
    exit(1)
}
