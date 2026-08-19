import SwiftUI

enum AppAppearance {
    static let accent = Color(red: 0.45, green: 0.18, blue: 0.20)
    static let parchment = Color(red: 0.97, green: 0.95, blue: 0.91)
    static let ink = Color(red: 0.08, green: 0.07, blue: 0.06)
    static let locationPill = Color(red: 0.16, green: 0.13, blue: 0.12)
    static let apparatus = Color(red: 0.48, green: 0.45, blue: 0.42)
    static let sectionLabel = Color(red: 0.42, green: 0.40, blue: 0.38)

    static func displaySerif(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .serif)
    }

    static func readerSerif(_ size: CGFloat) -> Font {
        .system(size: size, weight: .regular, design: .serif)
    }

    static func uiSans(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .default)
    }
}
