import SwiftUI

struct BrowseView: View {
    @Environment(CatalogStore.self) private var catalog
    @State private var collapsedChapters: Set<String> = []
    @State private var showingAbout = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 48) {
                ForEach(catalog.parts) { part in
                    TOCPartSection(part: part, collapsedChapters: $collapsedChapters)
                }

                Button("About") {
                    showingAbout = true
                }
                .font(AppAppearance.uiSans(13))
                .foregroundStyle(AppAppearance.accent)
                .frame(maxWidth: .infinity)
                .padding(.top, 8)
                .accessibilityLabel("About this app")
            }
            .padding(.horizontal, 36)
            .padding(.top, 20)
            .padding(.bottom, 64)
        }
        .readerChrome()
        .navigationTitle("Precious Promises")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showingAbout) {
            NavigationStack {
                AboutView()
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Button("Done") { showingAbout = false }
                        }
                    }
            }
            .tint(AppAppearance.accent)
            .presentationBackground(AppAppearance.parchment)
        }
        .navigationDestination(for: ThemeRoute.self) { route in
            ThemePageView(route: route)
        }
    }

}

/// Named views (not `some View` helpers) so nested TOC rows do not form an opaque-type cycle.
private struct TOCPartSection: View {
    let part: CatalogPart
    @Binding var collapsedChapters: Set<String>

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            Text(partLabel)
                .font(AppAppearance.uiSans(11, weight: .semibold))
                .tracking(2.4)
                .foregroundStyle(AppAppearance.sectionLabel)
                .frame(maxWidth: .infinity)

            ForEach(part.chapters) { chapter in
                TOCChapterSection(chapter: chapter, collapsedChapters: $collapsedChapters)
            }
        }
    }

    private var partLabel: String {
        switch part.id {
        case "part-1": return "PART I"
        case "part-2": return "PART II"
        default: return "APPENDIX"
        }
    }
}

private struct TOCChapterSection: View {
    let chapter: CatalogChapter
    @Binding var collapsedChapters: Set<String>

    private var collapsed: Bool {
        collapsedChapters.contains(chapter.id)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            VStack(spacing: 4) {
                Text("Chapter \(chapter.number)")
                    .font(AppAppearance.displaySerif(17))
                    .foregroundStyle(AppAppearance.ink)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
                    .accessibilityAddTraits(.isHeader)

                Button {
                    if collapsed {
                        collapsedChapters.remove(chapter.id)
                    } else {
                        collapsedChapters.insert(chapter.id)
                    }
                } label: {
                    Text(chapter.title)
                        .font(AppAppearance.displaySerif(28))
                        .foregroundStyle(AppAppearance.ink)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 4)
                }
                .buttonStyle(.plain)
                .accessibilityLabel("Chapter \(chapter.number), \(chapter.title)")
                .accessibilityHint(collapsed ? "Expands this chapter" : "Collapses this chapter")
            }

            if !collapsed {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(chapter.themes) { theme in
                        TOCThemeNode(theme: theme, indent: 0)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
    }
}

private struct TOCThemeNode: View {
    let theme: CatalogTheme
    let indent: Int
    @Environment(CatalogStore.self) private var catalog

    private let numberColumn: CGFloat = 32
    private let titleGutter: CGFloat = 8
    private let childIndent: CGFloat = 18

    private var isSubtheme: Bool { indent > 0 }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            NavigationLink(value: catalog.route(for: theme)) {
                HStack(alignment: .firstTextBaseline, spacing: titleGutter) {
                    if let number = theme.number {
                        Text(number + ".")
                            .font(AppAppearance.displaySerif(19))
                            .foregroundStyle(AppAppearance.ink)
                            .frame(width: numberColumn, alignment: .trailing)
                        Text(theme.title)
                            .font(AppAppearance.displaySerif(19))
                            .foregroundStyle(AppAppearance.ink)
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    } else {
                        Text(theme.title)
                            .font(AppAppearance.displaySerif(isSubtheme ? 16 : 19))
                            .foregroundStyle(AppAppearance.ink.opacity(isSubtheme ? 0.58 : 1))
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.leading, numberColumn + titleGutter + CGFloat(indent) * childIndent)
                    }
                }
                .padding(.vertical, 3)
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            ForEach(theme.children) { child in
                // AnyView breaks the `some View` cycle at the only recursive TOC edge.
                AnyView(TOCThemeNode(theme: child, indent: indent + 1))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct ThemePageView: View {
    let route: ThemeRoute
    @Environment(CatalogStore.self) private var catalog

    var body: some View {
        Group {
            if let theme = catalog.theme(id: route.themeID) {
                ThemeReader(theme: theme, route: route)
            } else {
                ContentUnavailableView("Theme missing", systemImage: "book.closed")
            }
        }
    }
}

private struct ThemeReader: View {
    let theme: CatalogTheme
    let route: ThemeRoute
    @Environment(CatalogStore.self) private var catalog
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    titleBlock
                        .padding(.bottom, theme.verses.isEmpty ? 8 : 16)

                    if !theme.verses.isEmpty {
                        verseColumn(theme.verses, heading: nil)
                    }

                    ForEach(theme.children) { child in
                        childBlock(child)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 48)
            }
            .background(AppAppearance.parchment.ignoresSafeArea())
            .onAppear {
                scroll(using: proxy)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .navigationBarBackButtonHidden(false)
        .toolbarBackground(AppAppearance.parchment, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .toolbar {
            ToolbarItem(placement: .principal) {
                Button {
                    dismiss()
                } label: {
                    Text(catalog.locationLabel(for: theme))
                        .font(AppAppearance.uiSans(11, weight: .semibold))
                        .foregroundStyle(AppAppearance.locationPillText)
                        .lineLimit(1)
                        .minimumScaleFactor(0.75)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(AppAppearance.locationPill, in: Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityLabel("Back to contents, \(catalog.locationLabel(for: theme))")
            }
        }
    }

    private var titleBlock: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let number = theme.number {
                Text("\(number).  \(theme.title)")
                    .font(AppAppearance.displaySerif(28))
                    .foregroundStyle(AppAppearance.ink)
            } else {
                Text(theme.title)
                    .font(AppAppearance.displaySerif(28))
                    .foregroundStyle(AppAppearance.ink)
            }
        }
    }

    private func childBlock(_ child: CatalogTheme) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(child.title.uppercased())
                .font(AppAppearance.uiSans(11, weight: .medium))
                .tracking(1.6)
                .foregroundStyle(AppAppearance.sectionLabel)
                .padding(.top, 20)
                .padding(.bottom, 8)
                .id(child.id)

            if !child.verses.isEmpty {
                verseColumn(child.verses, heading: nil)
            }

            ForEach(child.children) { grand in
                Text(grand.title)
                    .font(AppAppearance.uiSans(11, weight: .regular))
                    .foregroundStyle(AppAppearance.sectionLabel)
                    .padding(.top, 12)
                    .padding(.bottom, 6)
                    .padding(.leading, 20)
                    .id(grand.id)

                verseColumn(grand.verses, heading: nil)
                    .padding(.leading, 20)
            }
        }
    }

    private func verseColumn(_ verses: [CatalogVerse], heading: String?) -> some View {
        VStack(alignment: .leading, spacing: 11) {
            ForEach(verses) { verse in
                ReaderVerseBlock(verse: verse, emphasized: verse.id == route.highlightVerseID)
                    .id(verse.id)
            }
        }
    }

    private func scroll(using proxy: ScrollViewProxy) {
        if let verseID = route.highlightVerseID {
            proxy.scrollTo(verseID, anchor: .center)
        } else if let childID = route.highlightChildID {
            proxy.scrollTo(childID, anchor: .top)
        }
    }
}
