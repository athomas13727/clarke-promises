import SwiftUI

struct PartListView: View {
    @Environment(CatalogStore.self) private var catalog

    var body: some View {
        List {
            Section {
                Text("Samuel Clark of St Albans arranged the promises of Scripture under their proper heads. Browse the 1895 two-part book, plus the appendix on the Church.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .listRowBackground(AppAppearance.parchment)
            }

            ForEach(catalog.parts) { part in
                NavigationLink(value: part) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(part.title)
                            .font(.headline)
                        Text(part.summary)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        Text(partStats(part))
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle("Clarke's Promises")
        .navigationDestination(for: CatalogPart.self) { part in
            ChapterListView(part: part)
        }
        .navigationDestination(for: CatalogChapter.self) { chapter in
            ThemeListView(chapter: chapter)
        }
        .navigationDestination(for: CatalogTheme.self) { theme in
            VerseListView(theme: theme)
        }
        .navigationDestination(for: CatalogVerse.self) { verse in
            VerseDetailView(verse: verse)
        }
    }

    private func partStats(_ part: CatalogPart) -> String {
        let themes = part.chapters.reduce(0) { $0 + $1.themes.count }
        let verses = part.chapters.reduce(0) { $0 + $1.themes.reduce(0) { $0 + $1.verses.count } }
        return "\(part.chapters.count) chapters · \(themes) themes · \(verses) promises"
    }
}

struct ChapterListView: View {
    let part: CatalogPart

    var body: some View {
        List(part.chapters) { chapter in
            NavigationLink(value: chapter) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Chapter \(chapter.number)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(chapter.title)
                        .font(.headline)
                    Text("\(chapter.themes.count) themes")
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                }
                .padding(.vertical, 4)
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle(part.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ThemeListView: View {
    let chapter: CatalogChapter

    var body: some View {
        List(chapter.themes) { theme in
            NavigationLink(value: theme) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(theme.title)
                        .font(.headline)
                    Text("\(theme.verses.count) verses · 1895 p. \(theme.sourcePage)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle(chapter.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct VerseListView: View {
    let theme: CatalogTheme

    var body: some View {
        List(theme.verses) { verse in
            NavigationLink(value: verse) {
                VerseRow(verse: verse, showsTheme: false)
            }
        }
        .scrollContentBackground(.hidden)
        .background(AppAppearance.parchment)
        .navigationTitle(theme.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}
