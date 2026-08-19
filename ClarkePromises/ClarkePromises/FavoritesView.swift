import SwiftData
import SwiftUI

struct FavoritesView: View {
    @Environment(CatalogStore.self) private var catalog
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \FavoriteVerse.createdAt, order: .reverse) private var favorites: [FavoriteVerse]
    @State private var presentedTheme: ThemeRoute?

    var body: some View {
        List {
            ForEach(favorites, id: \.osis) { favorite in
                row(for: favorite)
                    .listRowInsets(EdgeInsets(top: 10, leading: 22, bottom: 10, trailing: 22))
                    .listRowSeparator(.hidden)
                    .listRowBackground(AppAppearance.parchment)
                    .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                        Button(role: .destructive) {
                            withAnimation {
                                modelContext.delete(favorite)
                            }
                        } label: {
                            Text("Remove")
                                .font(AppAppearance.uiSans(13, weight: .semibold))
                                .foregroundStyle(.white)
                        }
                        .tint(Color(uiColor: .systemRed))
                    }
            }
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)
        .scrollDisabled(favorites.isEmpty)
        .environment(\.defaultMinListRowHeight, 0)
        .overlay {
            if favorites.isEmpty {
                emptyColophon
            }
        }
        .readerChrome()
        .navigationTitle("Favorites")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(item: $presentedTheme) { route in
            ThemePageView(route: route)
        }
        .animation(.default, value: favorites.count)
    }

    private var emptyColophon: some View {
        Text("No saved promises.")
            .font(AppAppearance.citationSerif(17))
            .foregroundStyle(AppAppearance.inkSecondary)
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .accessibilityLabel("No saved promises.")
    }

    @ViewBuilder
    private func row(for favorite: FavoriteVerse) -> some View {
        if let verse = catalog.verse(osis: favorite.osis),
           let route = catalog.route(forOsis: favorite.osis) {
            FavoritePromiseRow(verse: verse)
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(Rectangle())
                .onTapGesture {
                    presentedTheme = route
                }
                .accessibilityAddTraits(.isButton)
                .accessibilityHint("Opens this promise")
        } else {
            FavoritePromiseRow(citation: favorite.displayRef, kjv: nil)
        }
    }
}

/// Theme-page verse block, slightly tighter. Filled star is a mark, not a control.
private struct FavoritePromiseRow: View {
    var citation: String
    var kjv: String?

    init(verse: CatalogVerse) {
        self.citation = verse.displayRef
        self.kjv = ReaderVerseBlock.displayKJV(verse.kjv)
    }

    init(citation: String, kjv: String?) {
        self.citation = citation
        self.kjv = kjv
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let kjv {
                Text(kjv)
                    .font(AppAppearance.readerSerif(19))
                    .foregroundStyle(AppAppearance.ink)
                    .lineSpacing(9)
                    .fixedSize(horizontal: false, vertical: true)
            }

            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text(citation)
                    .font(AppAppearance.citationSerif(13))
                    .foregroundStyle(AppAppearance.inkSecondary)
                Spacer(minLength: 8)
                Image(systemName: "star.fill")
                    .font(AppAppearance.uiSans(13))
                    .foregroundStyle(AppAppearance.accent)
                    .accessibilityHidden(true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
