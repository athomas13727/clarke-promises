import SwiftUI
import UIKit

enum AppAppearance {
    /// Burgundy is the only accent in both appearances.
    static let accent = adaptive(
        light: UIColor(red: 0.45, green: 0.18, blue: 0.20, alpha: 1),
        dark: UIColor(red: 0.64, green: 0.30, blue: 0.34, alpha: 1)
    )

    /// Page / chrome. Light parchment; dark warm charcoal, not iOS gray.
    static let parchment = adaptive(
        light: UIColor(red: 0.96, green: 0.94, blue: 0.89, alpha: 1),
        dark: UIColor(red: 0.11, green: 0.09, blue: 0.07, alpha: 1)
    )

    /// Body type. Light ink; dark dim cream.
    static let ink = adaptive(
        light: .black,
        dark: UIColor(red: 0.88, green: 0.84, blue: 0.74, alpha: 1)
    )

    static let locationPill = adaptive(
        light: UIColor(red: 0.14, green: 0.12, blue: 0.11, alpha: 1),
        dark: UIColor(red: 0.22, green: 0.18, blue: 0.14, alpha: 1)
    )

    static let locationPillText = adaptive(
        light: UIColor(red: 0.96, green: 0.94, blue: 0.89, alpha: 1),
        dark: UIColor(red: 0.88, green: 0.84, blue: 0.74, alpha: 1)
    )

    static let apparatus = adaptive(
        light: UIColor(red: 0.55, green: 0.52, blue: 0.49, alpha: 1),
        dark: UIColor(red: 0.64, green: 0.58, blue: 0.50, alpha: 1)
    )

    static let sectionLabel = adaptive(
        light: UIColor(red: 0.46, green: 0.44, blue: 0.41, alpha: 1),
        dark: UIColor(red: 0.70, green: 0.64, blue: 0.54, alpha: 1)
    )

    static func displaySerif(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .serif)
    }

    static func readerSerif(_ size: CGFloat) -> Font {
        .system(size: size, weight: .regular, design: .serif)
    }

    static func uiSans(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .default)
    }

    private static func adaptive(light: UIColor, dark: UIColor) -> Color {
        Color(uiColor: UIColor { traits in
            traits.userInterfaceStyle == .dark ? dark : light
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
