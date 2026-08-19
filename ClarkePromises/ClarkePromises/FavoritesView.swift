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
                    description: Text("Tap the star on any promise to save it on this device. Nothing is synced or sent anywhere.")
                )
                .listRowBackground(Color.clear)
            } else {
                ForEach(favorites, id: \.osis) { favorite in
                    if let verse = catalog.verse(osis: favorite.osis) {
                        NavigationLink(value: verse) {
                            VerseRow(verse: verse)
                        }
                    } else {
                        Text(favorite.displayRef)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle("Favorites")
        .navigationDestination(for: CatalogVerse.self) { verse in
            VerseDetailView(verse: verse)
        }
    }
}
