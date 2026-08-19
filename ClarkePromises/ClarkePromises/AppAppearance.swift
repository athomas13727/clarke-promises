import SwiftUI

enum AppAppearance {
    static let accent = Color(red: 0.45, green: 0.18, blue: 0.20)
    static let parchment = Color(red: 0.98, green: 0.96, blue: 0.92)
    static let ink = Color(red: 0.16, green: 0.12, blue: 0.10)

    static var verseFont: Font {
        .system(.body, design: .serif)
    }

    static var referenceFont: Font {
        .system(.headline, design: .serif)
    }
}
