import SwiftUI

enum AppAppearance {
    static let accent = Color(red: 0.45, green: 0.18, blue: 0.20)
    static let parchment = Color(red: 0.96, green: 0.94, blue: 0.89)
    static let ink = Color.black
    static let locationPill = Color(red: 0.14, green: 0.12, blue: 0.11)
    static let apparatus = Color(red: 0.55, green: 0.52, blue: 0.49)
    static let sectionLabel = Color(red: 0.46, green: 0.44, blue: 0.41)

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
