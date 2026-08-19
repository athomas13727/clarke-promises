import SwiftUI
import UIKit

enum AppAppearance {
    static let parchment = adaptive(light: 0xF4EFE6, dark: 0x1A1612)
    static let parchmentElevated = adaptive(light: 0xFAF7F0, dark: 0x262019)
    static let ink = adaptive(light: 0x1A1512, dark: 0xEDE6DA)
    static let inkSecondary = adaptive(light: 0x6F675E, dark: 0xA89F91)
    static let accent = adaptive(light: 0x732E33, dark: 0xC4787A)
    static let hairline = adaptive(light: 0xE4DDD2, dark: 0x3A322C)
    static let tabBar = adaptive(light: 0xF4EFE6, dark: 0x1A1612)
    static let locationPillFill = adaptive(light: 0x1A1512, dark: 0xEDE6DA)
    static let locationPillText = adaptive(light: 0xF4EFE6, dark: 0x1A1612)
    static let highlight = adaptive(light: 0xF0E2C8, dark: 0x4A3A28)

    static func displaySerif(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .serif)
    }

    static func readerSerif(_ size: CGFloat) -> Font {
        .system(size: size, weight: .regular, design: .serif)
    }

    static func citationSerif(_ size: CGFloat) -> Font {
        .system(size: size, weight: .regular, design: .serif).italic()
    }

    static func uiSans(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .default)
    }

    /// New York by name / serif descriptor — `Font.system(..., design: .serif)` at
    /// 12pt often resolves to SF, and `.tracking` can throw the face away.
    static func newYork(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        Font(uiNewYork(size: size, weight: weight))
    }

    static func uiNewYork(size: CGFloat, weight: Font.Weight) -> UIFont {
        let uiWeight: UIFont.Weight
        switch weight {
        case .bold, .heavy, .black: uiWeight = .bold
        case .semibold: uiWeight = .semibold
        case .medium: uiWeight = .medium
        default: uiWeight = .regular
        }
        let optical = size <= 14 ? "Small" : (size <= 24 ? "Medium" : "Large")
        let face: String
        switch uiWeight {
        case .bold, .heavy, .black: face = "Bold"
        case .semibold: face = "Semibold"
        case .medium: face = "Medium"
        default: face = "Regular"
        }
        let names = [
            "NewYork\(optical)-\(face)",
            ".NewYork\(optical)-\(face)",
            "NewYork-\(face)",
            ".NewYork-\(face)",
        ]
        for name in names {
            if let font = UIFont(name: name, size: size) {
                return font
            }
        }
        let base = UIFont.systemFont(ofSize: size, weight: uiWeight)
        if let descriptor = base.fontDescriptor.withDesign(.serif) {
            return UIFont(descriptor: descriptor, size: size)
        }
        return base
    }

    private static func hex(_ value: UInt32) -> UIColor {
        UIColor(
            red: CGFloat((value >> 16) & 0xFF) / 255,
            green: CGFloat((value >> 8) & 0xFF) / 255,
            blue: CGFloat(value & 0xFF) / 255,
            alpha: 1
        )
    }

    private static func adaptive(light: UInt32, dark: UInt32) -> Color {
        Color(uiColor: UIColor { traits in
            traits.userInterfaceStyle == .dark ? hex(dark) : hex(light)
        })
    }
}

extension View {
    func readerChrome() -> some View {
        background(AppAppearance.parchment.ignoresSafeArea())
            .toolbarBackground(AppAppearance.parchment, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
    }
}
