import SwiftData
import SwiftUI

struct ReaderVerseBlock: View {
    let verse: CatalogVerse
    var emphasized: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            (Text(verseNumber).font(AppAppearance.uiSans(10, weight: .medium))
                .baselineOffset(6)
                .foregroundColor(AppAppearance.apparatus)
            + Text("  " + verse.kjv)
                .font(AppAppearance.readerSerif(17.5))
                .foregroundColor(AppAppearance.ink))
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)

            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text(verse.displayRef)
                    .font(AppAppearance.uiSans(11))
                    .foregroundStyle(AppAppearance.apparatus)
                Spacer(minLength: 8)
                FavoriteStarButton(verse: verse)
                Link("Open in ESV", destination: ESVLink.esvOrgURL(for: verse))
                    .font(AppAppearance.uiSans(11, weight: .medium))
                    .foregroundStyle(AppAppearance.accent)
            }
        }
        .padding(.vertical, 2)
        .padding(.horizontal, emphasized ? 8 : 0)
        .background {
            if emphasized {
                AppAppearance.accent.opacity(0.07)
                    .padding(.horizontal, -8)
            }
        }
    }

    private var verseNumber: String {
        if let end = verse.endVerse, end != verse.verse {
            return "\(verse.verse)–\(end)"
        }
        return "\(verse.verse)"
    }
}

struct SearchHitRow: View {
    let hit: SearchHit

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(hit.theme.title)
                .font(AppAppearance.uiSans(12, weight: .medium))
                .foregroundStyle(AppAppearance.sectionLabel)
            Text(hit.verse.kjv)
                .font(AppAppearance.readerSerif(16))
                .foregroundStyle(AppAppearance.ink)
                .lineLimit(3)
            Text(hit.verse.displayRef)
                .font(AppAppearance.uiSans(11))
                .foregroundStyle(AppAppearance.apparatus)
        }
        .padding(.vertical, 4)
    }
}

struct FavoriteStarButton: View {
    let verse: CatalogVerse
    var themeID: String? = nil
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
                .font(AppAppearance.uiSans(12))
                .foregroundStyle(isFavorite ? AppAppearance.accent : AppAppearance.apparatus)
                .accessibilityLabel(isFavorite ? "Remove favorite" : "Add favorite")
        }
        .buttonStyle(.plain)
    }

    private var isFavorite: Bool {
        FavoritesStore.isFavorite(verse.osis, in: favorites)
    }
}
