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
