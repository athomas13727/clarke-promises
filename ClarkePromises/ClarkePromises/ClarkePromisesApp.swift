import SwiftData
import SwiftUI

@main
struct ClarkePromisesApp: App {
    @State private var catalog = CatalogStore.loadFromBundle()

    var body: some Scene {
        WindowGroup {
            RootTabView()
                .environment(catalog)
                .tint(AppAppearance.accent)
        }
        .modelContainer(for: FavoriteVerse.self)
    }
}
