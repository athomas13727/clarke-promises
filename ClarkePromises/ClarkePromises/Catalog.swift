import Foundation
import Observation

struct CatalogFile: Codable, Hashable {
    var meta: CatalogMeta
    var parts: [CatalogPart]
}

struct CatalogMeta: Codable, Hashable {
    var title: String
    var alsoCalled: [String]
    var author: String
    var authorYears: String
    var place: String
    var edition: String
    var source: String
    var structure: String
    var corpusStatus: String
    var kjvSource: String
    var excluded: [String]
    var themeCount: Int
    var verseEntryCount: Int
    var emptyThemesOmitted: [String]
}

struct CatalogPart: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    var summary: String
    var chapters: [CatalogChapter]
}

struct CatalogChapter: Codable, Hashable, Identifiable {
    var id: String
    var number: Int
    var title: String
    var themes: [CatalogTheme]
}

struct CatalogTheme: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    var sourcePage: Int
    var verses: [CatalogVerse]
}

struct CatalogVerse: Codable, Hashable, Identifiable {
    var id: String
    var osis: String
    var displayRef: String
    var book: String
    var chapter: Int
    var verse: Int
    var endVerse: Int?
    var kjv: String
}

@MainActor
@Observable
final class CatalogStore {
    let file: CatalogFile

    init(file: CatalogFile) {
        self.file = file
    }

    static func loadFromBundle() -> CatalogStore {
        guard let url = Bundle.main.url(forResource: "clarke-promises", withExtension: "json") else {
            fatalError("clarke-promises.json is missing from the app bundle.")
        }
        do {
            let data = try Data(contentsOf: url)
            let decoded = try JSONDecoder().decode(CatalogFile.self, from: data)
            return CatalogStore(file: decoded)
        } catch {
            fatalError("Unable to read clarke-promises.json: \(error)")
        }
    }

    var parts: [CatalogPart] { file.parts }
    var meta: CatalogMeta { file.meta }

    var allThemes: [CatalogTheme] {
        parts.flatMap { $0.chapters.flatMap(\.themes) }
    }

    var allVerses: [CatalogVerse] {
        allThemes.flatMap(\.verses)
    }

    func part(containing theme: CatalogTheme) -> CatalogPart? {
        parts.first { part in
            part.chapters.contains { chapter in
                chapter.themes.contains { $0.id == theme.id }
            }
        }
    }

    func chapter(containing theme: CatalogTheme) -> CatalogChapter? {
        for part in parts {
            if let chapter = part.chapters.first(where: { $0.themes.contains(where: { $0.id == theme.id }) }) {
                return chapter
            }
        }
        return nil
    }

    func theme(containing verseID: String) -> CatalogTheme? {
        allThemes.first { theme in
            theme.verses.contains { $0.id == verseID }
        }
    }

    func verse(osis: String) -> CatalogVerse? {
        allVerses.first { $0.osis == osis }
    }

    func search(query: String) -> [SearchHit] {
        let needle = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard needle.count >= 2 else { return [] }
        return SearchIndex.hits(in: file, query: needle)
    }
}

struct SearchHit: Identifiable, Hashable {
    var id: String { verse.id + "|" + theme.id }
    var verse: CatalogVerse
    var theme: CatalogTheme
    var chapterTitle: String
    var partTitle: String
}

enum SearchIndex {
    static func hits(in file: CatalogFile, query: String) -> [SearchHit] {
        let terms = query.lowercased().split { $0.isWhitespace }.map(String.init)
        guard !terms.isEmpty else { return [] }

        var results: [SearchHit] = []
        for part in file.parts {
            for chapter in part.chapters {
                for theme in chapter.themes {
                    let themeBlob = theme.title.lowercased()
                    for verse in theme.verses {
                        let haystack = [
                            themeBlob,
                            verse.displayRef.lowercased(),
                            verse.osis.lowercased(),
                            verse.book.lowercased(),
                            verse.kjv.lowercased()
                        ].joined(separator: " ")
                        if terms.allSatisfy({ haystack.contains($0) }) {
                            results.append(
                                SearchHit(
                                    verse: verse,
                                    theme: theme,
                                    chapterTitle: chapter.title,
                                    partTitle: part.title
                                )
                            )
                        }
                    }
                }
            }
        }
        return results
    }
}
