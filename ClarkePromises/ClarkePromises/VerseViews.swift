import SwiftData
import SwiftUI

struct ReaderVerseBlock: View {
    let verse: CatalogVerse
    var themeID: String? = nil
    var emphasized: Bool = false

    @ScaledMetric(relativeTo: .body) private var verseSize: CGFloat = 19
    @ScaledMetric(relativeTo: .body) private var verseLine: CGFloat = 28
    @ScaledMetric(relativeTo: .footnote) private var citationSize: CGFloat = 13
    @ScaledMetric(relativeTo: .caption) private var esvSize: CGFloat = 12
    @ScaledMetric(relativeTo: .body) private var starSize: CGFloat = 17

    @Environment(\.openURL) private var openURL

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(Self.displayKJV(verse.kjv))
                .font(AppAppearance.readerSerif(verseSize))
                .foregroundStyle(AppAppearance.ink)
                .lineSpacing(max(0, verseLine - verseSize))
                .fixedSize(horizontal: false, vertical: true)

            HStack(alignment: .center, spacing: 4) {
                Text(verse.displayRef)
                    .font(AppAppearance.citationSerif(citationSize))
                    .foregroundStyle(AppAppearance.inkSecondary)
                Spacer(minLength: 8)
                FavoriteStarButton(verse: verse, themeID: themeID, pointSize: starSize)
                Button {
                    openURL(ESVLink.esvOrgURL(for: verse))
                } label: {
                    Text("ESV")
                        .font(AppAppearance.uiSans(esvSize, weight: .medium))
                        .foregroundStyle(AppAppearance.inkSecondary)
                        .frame(minWidth: 44, minHeight: 44)
                        .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .accessibilityLabel("Open in ESV")
            }
            .padding(.top, 10)
        }
        .padding(.horizontal, emphasized ? 8 : 0)
        .background {
            if emphasized {
                AppAppearance.highlight
                    .padding(.horizontal, -8)
            }
        }
    }

    /// Running KJV only: no wrapping quotes, no leading in-text verse numbers.
    static func displayKJV(_ text: String) -> String {
        var t = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let wraps = CharacterSet(charactersIn: "\"“”‘’")
        while let scalar = t.unicodeScalars.first, wraps.contains(scalar) {
            t.removeFirst()
            t = t.trimmingCharacters(in: .whitespaces)
        }
        while let scalar = t.unicodeScalars.last, wraps.contains(scalar) {
            t.removeLast()
            t = t.trimmingCharacters(in: .whitespaces)
        }
        if let match = t.range(of: #"^\d+[.)]?\s+"#, options: .regularExpression) {
            t.removeSubrange(match)
        }
        return t.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

struct SearchHitRow: View {
    let hit: SearchHit

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(hit.theme.title)
                .font(AppAppearance.uiSans(12, weight: .medium))
                .foregroundStyle(AppAppearance.inkSecondary)
            Text(ReaderVerseBlock.displayKJV(hit.verse.kjv))
                .font(AppAppearance.readerSerif(16))
                .foregroundStyle(AppAppearance.ink)
                .lineLimit(3)
            Text(hit.verse.displayRef)
                .font(AppAppearance.uiSans(11))
                .foregroundStyle(AppAppearance.inkSecondary)
        }
        .padding(.vertical, 4)
    }
}

struct FavoriteStarButton: View {
    let verse: CatalogVerse
    var themeID: String? = nil
    var pointSize: CGFloat = 17
    @Environment(\.modelContext) private var modelContext
    @Query private var favorites: [FavoriteVerse]

    var body: some View {
        Button {
            FavoritesStore.toggle(
                verse: verse,
                themeID: themeID,
                favorites: favorites,
                context: modelContext
            )
        } label: {
            Image(systemName: isFavorite ? "star.fill" : "star")
                .font(AppAppearance.uiSans(pointSize))
                .foregroundStyle(isFavorite ? AppAppearance.accent : AppAppearance.inkSecondary)
                .frame(width: 44, height: 44)
                .contentShape(Rectangle())
                .accessibilityLabel(isFavorite ? "Remove favorite" : "Add favorite")
        }
        .buttonStyle(.plain)
    }

    private var isFavorite: Bool {
        FavoritesStore.isFavorite(verse.osis, in: favorites)
    }
}
