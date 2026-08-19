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
    var nestedHeads: Bool?
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
    var number: String?
    var title: String
    var sourcePage: Int
    var verses: [CatalogVerse]
    var children: [CatalogTheme]

    enum CodingKeys: String, CodingKey {
        case id, number, title, sourcePage, verses, children
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        number = try container.decodeIfPresent(String.self, forKey: .number)
        title = try container.decode(String.self, forKey: .title)
        sourcePage = try container.decode(Int.self, forKey: .sourcePage)
        verses = try container.decodeIfPresent([CatalogVerse].self, forKey: .verses) ?? []
        children = try container.decodeIfPresent([CatalogTheme].self, forKey: .children) ?? []
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encodeIfPresent(number, forKey: .number)
        try container.encode(title, forKey: .title)
        try container.encode(sourcePage, forKey: .sourcePage)
        if !verses.isEmpty {
            try container.encode(verses, forKey: .verses)
        }
        if !children.isEmpty {
            try container.encode(children, forKey: .children)
        }
    }

    var isNumbered: Bool { number != nil }

    func contains(themeID: String) -> Bool {
        if id == themeID { return true }
        return children.contains { $0.contains(themeID: themeID) }
    }

    func contains(verseID: String) -> Bool {
        if verses.contains(where: { $0.id == verseID }) { return true }
        return children.contains { $0.contains(verseID: verseID) }
    }
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

struct ThemeRoute: Hashable {
    var themeID: String
    var highlightChildID: String?
    var highlightVerseID: String?
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
        parts.flatMap { part in
            part.chapters.flatMap { flatten($0.themes) }
        }
    }

    func flatten(_ themes: [CatalogTheme]) -> [CatalogTheme] {
        themes.flatMap { [$0] + flatten($0.children) }
    }

    func theme(id: String) -> CatalogTheme? {
        allThemes.first { $0.id == id }
    }

    func pageTheme(for theme: CatalogTheme) -> CatalogTheme {
        if theme.isNumbered { return theme }
        for part in parts {
            for chapter in part.chapters {
                if let page = numberedAncestor(in: chapter.themes, containing: theme.id) {
                    return page
                }
            }
        }
        return theme
    }

    func numberedAncestor(in themes: [CatalogTheme], containing themeID: String) -> CatalogTheme? {
        for theme in themes {
            if theme.id == themeID { return theme }
            if theme.contains(themeID: themeID) {
                if theme.isNumbered { return theme }
                if let nested = numberedAncestor(in: theme.children, containing: themeID) {
                    return nested
                }
                return theme
            }
        }
        return nil
    }

    func theme(containingVerseID verseID: String) -> CatalogTheme? {
        allThemes.first { $0.verses.contains { $0.id == verseID } }
    }

    func theme(containingOsis osis: String) -> CatalogTheme? {
        allThemes.first { $0.verses.contains { $0.osis == osis } }
    }

    func verse(osis: String) -> CatalogVerse? {
        for theme in allThemes {
            if let verse = theme.verses.first(where: { $0.osis == osis }) {
                return verse
            }
        }
        return nil
    }

    func placement(of theme: CatalogTheme) -> (CatalogPart, CatalogChapter)? {
        for part in parts {
            for chapter in part.chapters {
                if chapter.themes.contains(where: { $0.contains(themeID: theme.id) }) {
                    return (part, chapter)
                }
            }
        }
        return nil
    }

    func locationLabel(for theme: CatalogTheme) -> String {
        let page = pageTheme(for: theme)
        guard let (part, chapter) = placement(of: page) else {
            return page.title
        }
        let partMark: String
        switch part.id {
        case "part-1": partMark = "I"
        case "part-2": partMark = "II"
        default: partMark = "APP."
        }
        return "\(partMark)  ·  Ch. \(chapter.number)  ·  \(page.title)"
    }

    func route(for theme: CatalogTheme) -> ThemeRoute {
        let page = pageTheme(for: theme)
        return ThemeRoute(
            themeID: page.id,
            highlightChildID: page.id == theme.id ? nil : theme.id,
            highlightVerseID: nil
        )
    }

    func route(forOsis osis: String) -> ThemeRoute? {
        guard let leaf = theme(containingOsis: osis),
              let verse = leaf.verses.first(where: { $0.osis == osis }) else {
            return nil
        }
        let page = pageTheme(for: leaf)
        return ThemeRoute(
            themeID: page.id,
            highlightChildID: page.id == leaf.id ? nil : leaf.id,
            highlightVerseID: verse.id
        )
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
    var pageTheme: CatalogTheme
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
                walk(chapter.themes, part: part, chapter: chapter, ancestors: [], terms: terms, into: &results)
            }
        }
        return results
    }

    private static func walk(
        _ themes: [CatalogTheme],
        part: CatalogPart,
        chapter: CatalogChapter,
        ancestors: [CatalogTheme],
        terms: [String],
        into results: inout [SearchHit]
    ) {
        for theme in themes {
            let page = theme.number != nil ? theme : (ancestors.last(where: { $0.number != nil }) ?? theme)
            let themeBlob = ([theme.title] + ancestors.map(\.title)).joined(separator: " ").lowercased()
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
                            pageTheme: page,
                            chapterTitle: chapter.title,
                            partTitle: part.title
                        )
                    )
                }
            }
            walk(
                theme.children,
                part: part,
                chapter: chapter,
                ancestors: ancestors + [theme],
                terms: terms,
                into: &results
            )
        }
    }
}
