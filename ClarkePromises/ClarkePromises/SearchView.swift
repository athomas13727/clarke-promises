import SwiftUI

struct SearchView: View {
    @Environment(CatalogStore.self) private var catalog
    @State private var query = ""

    var body: some View {
        List {
            if query.trimmingCharacters(in: .whitespacesAndNewlines).count < 2 {
                ContentUnavailableView(
                    "Search the promises",
                    systemImage: "magnifyingglass",
                    description: Text("Find Clark's heads, verse references, or King James wording. Try “access”, “Psalm 23”, or “shepherd”.")
                )
                .listRowBackground(Color.clear)
            } else if hits.isEmpty {
                ContentUnavailableView.search(text: query)
                    .listRowBackground(Color.clear)
            } else {
                Section("\(hits.count) matches") {
                    ForEach(hits) { hit in
                        NavigationLink(value: hit.verse) {
                            VerseRow(verse: hit.verse, showsTheme: true, themeTitle: hit.theme.title)
                        }
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle("Search")
        .searchable(text: $query, prompt: "Themes, references, KJV text")
        .navigationDestination(for: CatalogVerse.self) { verse in
            VerseDetailView(verse: verse)
        }
    }

    private var hits: [SearchHit] {
        catalog.search(query: query)
    }
}
