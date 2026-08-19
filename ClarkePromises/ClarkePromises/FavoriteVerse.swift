import Foundation
import SwiftData

@Model
final class FavoriteVerse {
    @Attribute(.unique) var osis: String
    var displayRef: String
    var themeID: String = ""
    var createdAt: Date

    init(osis: String, displayRef: String, themeID: String = "", createdAt: Date = .now) {
        self.osis = osis
        self.displayRef = displayRef
        self.themeID = themeID
        self.createdAt = createdAt
    }
}

enum FavoritesStore {
    static func isFavorite(_ osis: String, in favorites: [FavoriteVerse]) -> Bool {
        favorites.contains { $0.osis == osis }
    }

    @MainActor
    static func toggle(
        verse: CatalogVerse,
        themeID: String? = nil,
        favorites: [FavoriteVerse],
        context: ModelContext
    ) {
        if let existing = favorites.first(where: { $0.osis == verse.osis }) {
            context.delete(existing)
        } else {
            context.insert(
                FavoriteVerse(
                    osis: verse.osis,
                    displayRef: verse.displayRef,
                    themeID: themeID ?? ""
                )
            )
        }
    }
}
