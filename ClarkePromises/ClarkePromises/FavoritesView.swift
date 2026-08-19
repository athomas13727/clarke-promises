import SwiftData
import SwiftUI

struct FavoritesView: View {
    @Environment(CatalogStore.self) private var catalog
    @Query(sort: \FavoriteVerse.createdAt, order: .reverse) private var favorites: [FavoriteVerse]

    var body: some View {
        List {
            if favorites.isEmpty {
                ContentUnavailableView(
                    "No favorites yet",
                    systemImage: "star",
                    description: Text("Tap the star beside any promise. It stays on this device.")
                )
                .listRowBackground(Color.clear)
            } else {
                ForEach(favorites, id: \.osis) { favorite in
                    if let route = catalog.route(forOsis: favorite.osis),
                       let verse = catalog.verse(osis: favorite.osis),
                       let theme = catalog.theme(containingOsis: favorite.osis) {
                        NavigationLink(value: route) {
                            SearchHitRow(
                                hit: SearchHit(
                                    verse: verse,
                                    theme: theme,
                                    pageTheme: catalog.pageTheme(for: theme),
                                    chapterTitle: "",
                                    partTitle: ""
                                )
                            )
                        }
                    } else {
                        Text(favorite.displayRef)
                            .font(AppAppearance.uiSans(13))
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle("Favorites")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(for: ThemeRoute.self) { route in
            ThemePageView(route: route)
        }
    }
}
