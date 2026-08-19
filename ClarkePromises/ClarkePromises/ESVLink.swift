import Foundation

/// Outbound Bible Gateway versions. Never fetch or store these wordings in-app.
enum BibleGatewayVersion: String, CaseIterable, Identifiable {
    case esv = "ESV"
    case nasb = "NASB"
    case niv = "NIV"

    var id: String { rawValue }
}

/// Builds outbound links to licensed text hosted elsewhere.
/// This app never downloads, caches, or stores ESV (or NASB/NIV/NET) wording.
enum ESVLink {
    static func esvOrgURL(for verse: CatalogVerse) -> URL {
        esvOrgURL(book: verse.book, chapter: verse.chapter, verse: verse.verse, endVerse: verse.endVerse)
    }

    static func esvOrgURL(book: String, chapter: Int, verse: Int, endVerse: Int?) -> URL {
        let name = esvOrgBookName(book)
        let ref: String
        if let endVerse, endVerse != verse {
            ref = "\(name)+\(chapter):\(verse)-\(endVerse)"
        } else {
            ref = "\(name)+\(chapter):\(verse)"
        }
        let encoded = ref.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? ref
        return URL(string: "https://www.esv.org/\(encoded)/")!
    }

    /// YouVersion / bible.com translation id 59 is ESV.
    static func bibleDotComURL(for verse: CatalogVerse) -> URL {
        let code = youVersionCode(verse.book)
        let path = "\(code).\(verse.chapter).\(verse.verse)"
        return URL(string: "https://www.bible.com/bible/59/\(path)")!
    }

    static func esvOrgBookName(_ book: String) -> String {
        switch book {
        case "Psalms": return "Psalm"
        case "Song of Solomon": return "Song+of+Solomon"
        default: return book.replacingOccurrences(of: " ", with: "+")
        }
    }

    /// Bible Gateway passage page. Search is the reference only — no translation text.
    static func bibleGatewayURL(for verse: CatalogVerse, version: BibleGatewayVersion) -> URL {
        bibleGatewayURL(
            book: verse.book,
            chapter: verse.chapter,
            verse: verse.verse,
            endVerse: verse.endVerse,
            version: version
        )
    }

    static func bibleGatewayURL(
        book: String,
        chapter: Int,
        verse: Int,
        endVerse: Int?,
        version: BibleGatewayVersion
    ) -> URL {
        let search: String
        if let endVerse, endVerse != verse {
            search = "\(book) \(chapter):\(verse)-\(endVerse)"
        } else {
            search = "\(book) \(chapter):\(verse)"
        }
        var comps = URLComponents()
        comps.scheme = "https"
        comps.host = "www.biblegateway.com"
        comps.path = "/passage/"
        comps.queryItems = [
            URLQueryItem(name: "search", value: search),
            URLQueryItem(name: "version", value: version.rawValue),
        ]
        return comps.url!
    }

    static func youVersionCode(_ book: String) -> String {
        let map: [String: String] = [
            "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM",
            "Deuteronomy": "DEU", "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT",
            "1 Samuel": "1SA", "2 Samuel": "2SA", "1 Kings": "1KI", "2 Kings": "2KI",
            "1 Chronicles": "1CH", "2 Chronicles": "2CH", "Ezra": "EZR", "Nehemiah": "NEH",
            "Esther": "EST", "Job": "JOB", "Psalms": "PSA", "Proverbs": "PRO",
            "Ecclesiastes": "ECC", "Song of Solomon": "SNG", "Isaiah": "ISA",
            "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
            "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA",
            "Jonah": "JON", "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB",
            "Zephaniah": "ZEP", "Haggai": "HAG", "Zechariah": "ZEC", "Malachi": "MAL",
            "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN",
            "Acts": "ACT", "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO",
            "Galatians": "GAL", "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
            "1 Thessalonians": "1TH", "2 Thessalonians": "2TH", "1 Timothy": "1TI",
            "2 Timothy": "2TI", "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB",
            "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE", "1 John": "1JN",
            "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV"
        ]
        return map[book] ?? "JHN"
    }
}
