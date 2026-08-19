import SwiftUI

struct RootTabView: View {
    var body: some View {
        TabView {
            NavigationStack {
                BrowseView()
            }
            .tabItem {
                Label("Browse", systemImage: "book.closed")
            }

            NavigationStack {
                SearchView()
            }
            .tabItem {
                Label("Search", systemImage: "magnifyingglass")
            }

            NavigationStack {
                FavoritesView()
            }
            .tabItem {
                Label("Favorites", systemImage: "star")
            }
        }
    }
}
