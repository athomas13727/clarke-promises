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
                    description: Text("Find Clark's heads, references, or King James wording.")
                )
                .listRowBackground(Color.clear)
            } else if hits.isEmpty {
                ContentUnavailableView.search(text: query)
                    .listRowBackground(Color.clear)
            } else {
                ForEach(hits) { hit in
                    NavigationLink(value: route(for: hit)) {
                        SearchHitRow(hit: hit)
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle("Search")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(AppAppearance.parchment, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .searchable(text: $query, prompt: "Themes, references, KJV text")
        .navigationDestination(for: ThemeRoute.self) { route in
            ThemePageView(route: route)
        }
    }

    private var hits: [SearchHit] {
        catalog.search(query: query)
    }

    private func route(for hit: SearchHit) -> ThemeRoute {
        ThemeRoute(
            themeID: hit.pageTheme.id,
            highlightChildID: hit.pageTheme.id == hit.theme.id ? nil : hit.theme.id,
            highlightVerseID: hit.verse.id
        )
    }
}
