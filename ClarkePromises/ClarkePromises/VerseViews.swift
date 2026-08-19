import SwiftData
import SwiftUI

struct VerseRow: View {
    let verse: CatalogVerse
    var showsTheme: Bool = false
    var themeTitle: String? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(verse.displayRef)
                    .font(AppAppearance.referenceFont)
                Spacer()
                FavoriteStarButton(verse: verse)
                    .buttonStyle(.plain)
            }
            Text(verse.kjv)
                .font(AppAppearance.verseFont)
                .foregroundStyle(AppAppearance.ink)
                .lineLimit(4)
            if showsTheme, let themeTitle {
                Text(themeTitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct VerseDetailView: View {
    let verse: CatalogVerse
    @Environment(CatalogStore.self) private var catalog

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(verse.displayRef)
                    .font(.system(.title2, design: .serif).weight(.semibold))

                Text("King James Version")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Text(verse.kjv)
                    .font(.system(.title3, design: .serif))
                    .foregroundStyle(AppAppearance.ink)
                    .lineSpacing(6)

                if let theme = catalog.theme(containing: verse.id) {
                    LabeledContent("Clark's head") {
                        Text(theme.title)
                            .multilineTextAlignment(.trailing)
                    }
                    if let part = catalog.part(containing: theme),
                       let chapter = catalog.chapter(containing: theme) {
                        LabeledContent("Place in the book") {
                            Text("\(part.title), ch. \(chapter.number)")
                                .multilineTextAlignment(.trailing)
                        }
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Link(destination: ESVLink.esvOrgURL(for: verse)) {
                        Label("Open in ESV", systemImage: "arrow.up.right.square")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)

                    Link(destination: ESVLink.bibleDotComURL(for: verse)) {
                        Label("Open ESV on bible.com", systemImage: "safari")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Text("ESV text is © Crossway. This app does not bundle, cache, or store it. The link opens another app or Safari.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
                .padding(.top, 8)
            }
            .padding()
        }
        .background(AppAppearance.parchment)
        .navigationTitle(verse.displayRef)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                FavoriteStarButton(verse: verse)
            }
        }
    }
}

struct FavoriteStarButton: View {
    let verse: CatalogVerse
    @Environment(\.modelContext) private var modelContext
    @Query private var favorites: [FavoriteVerse]

    var body: some View {
        Button {
            FavoritesStore.toggle(verse: verse, favorites: favorites, context: modelContext)
        } label: {
            Image(systemName: isFavorite ? "star.fill" : "star")
                .foregroundStyle(isFavorite ? Color.yellow : AppAppearance.accent)
                .accessibilityLabel(isFavorite ? "Remove favorite" : "Add favorite")
        }
    }

    private var isFavorite: Bool {
        FavoritesStore.isFavorite(verse.osis, in: favorites)
    }
}
