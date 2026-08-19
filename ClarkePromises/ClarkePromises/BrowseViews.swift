import SwiftUI

struct BrowseView: View {
    @Environment(CatalogStore.self) private var catalog
    @State private var collapsedChapters: Set<String> = []
    @State private var showingAbout = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 36) {
                ForEach(catalog.parts) { part in
                    partBlock(part)
                }
            }
            .padding(.horizontal, 28)
            .padding(.top, 12)
            .padding(.bottom, 48)
        }
        .background(AppAppearance.parchment.ignoresSafeArea())
        .navigationTitle("Precious Promises")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    showingAbout = true
                } label: {
                    Image(systemName: "info.circle")
                }
                .accessibilityLabel("About")
            }
        }
        .sheet(isPresented: $showingAbout) {
            NavigationStack {
                AboutView()
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Button("Done") { showingAbout = false }
                        }
                    }
            }
        }
        .navigationDestination(for: ThemeRoute.self) { route in
            ThemePageView(route: route)
        }
    }

    private func partBlock(_ part: CatalogPart) -> some View {
        VStack(alignment: .leading, spacing: 22) {
            Text(partLabel(part))
                .font(AppAppearance.uiSans(11, weight: .semibold))
                .tracking(2.2)
                .foregroundStyle(AppAppearance.sectionLabel)
                .frame(maxWidth: .infinity)

            ForEach(part.chapters) { chapter in
                chapterBlock(chapter)
            }
        }
    }

    private func chapterBlock(_ chapter: CatalogChapter) -> some View {
        let collapsed = collapsedChapters.contains(chapter.id)
        return VStack(alignment: .leading, spacing: 14) {
            Button {
                if collapsed {
                    collapsedChapters.remove(chapter.id)
                } else {
                    collapsedChapters.insert(chapter.id)
                }
            } label: {
                Text(chapter.title)
                    .font(AppAppearance.displaySerif(26))
                    .foregroundStyle(AppAppearance.ink)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 4)
            }
            .buttonStyle(.plain)
            .accessibilityHint(collapsed ? "Expands this chapter" : "Collapses this chapter")

            if !collapsed {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(chapter.themes) { theme in
                        themeRows(theme, indent: 0)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func themeRows(_ theme: CatalogTheme, indent: Int) -> some View {
        NavigationLink(value: catalog.route(for: theme)) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                if let number = theme.number {
                    Text(number + ".")
                        .font(AppAppearance.displaySerif(18))
                        .foregroundStyle(AppAppearance.ink)
                        .frame(width: 36, alignment: .trailing)
                    Text(theme.title)
                        .font(AppAppearance.displaySerif(18))
                        .foregroundStyle(AppAppearance.ink)
                        .multilineTextAlignment(.leading)
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    Text(theme.title)
                        .font(AppAppearance.displaySerif(16))
                        .foregroundStyle(AppAppearance.ink.opacity(0.86))
                        .multilineTextAlignment(.leading)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.leading, CGFloat(36 + indent * 18))
                }
            }
            .padding(.vertical, 3)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)

        ForEach(theme.children) { child in
            themeRows(child, indent: indent + 1)
        }
    }

    private func partLabel(_ part: CatalogPart) -> String {
        switch part.id {
        case "part-1": return "PART I"
        case "part-2": return "PART II"
        default: return "APPENDIX"
        }
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

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    locationPill
                        .padding(.bottom, 22)

                    titleBlock
                        .padding(.bottom, theme.verses.isEmpty ? 10 : 22)

                    if !theme.verses.isEmpty {
                        verseColumn(theme.verses, heading: nil)
                    }

                    ForEach(theme.children) { child in
                        childBlock(child)
                    }
                }
                .padding(.horizontal, 26)
                .padding(.top, 10)
                .padding(.bottom, 56)
            }
            .background(AppAppearance.parchment.ignoresSafeArea())
            .onAppear {
                scroll(using: proxy)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text(shortTitle)
                    .font(AppAppearance.uiSans(13, weight: .semibold))
                    .foregroundStyle(AppAppearance.accent)
                    .lineLimit(1)
            }
        }
    }

    private var locationPill: some View {
        Text(catalog.locationLabel(for: theme))
            .font(AppAppearance.uiSans(11, weight: .semibold))
            .tracking(0.4)
            .foregroundStyle(AppAppearance.parchment)
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(AppAppearance.locationPill, in: Capsule())
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
                .font(AppAppearance.uiSans(12, weight: .medium))
                .tracking(1.4)
                .foregroundStyle(AppAppearance.sectionLabel)
                .padding(.top, 26)
                .padding(.bottom, 10)
                .id(child.id)

            if !child.verses.isEmpty {
                verseColumn(child.verses, heading: nil)
            }

            ForEach(child.children) { grand in
                Text(grand.title)
                    .font(AppAppearance.uiSans(12, weight: .regular))
                    .foregroundStyle(AppAppearance.sectionLabel)
                    .padding(.top, 16)
                    .padding(.bottom, 8)
                    .padding(.leading, 14)
                    .id(grand.id)

                verseColumn(grand.verses, heading: nil)
                    .padding(.leading, 14)
            }
        }
    }

    private func verseColumn(_ verses: [CatalogVerse], heading: String?) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            ForEach(verses) { verse in
                ReaderVerseBlock(verse: verse, emphasized: verse.id == route.highlightVerseID)
                    .id(verse.id)
            }
        }
    }

    private var shortTitle: String {
        theme.title
    }

    private func scroll(using proxy: ScrollViewProxy) {
        if let verseID = route.highlightVerseID {
            proxy.scrollTo(verseID, anchor: .center)
        } else if let childID = route.highlightChildID {
            proxy.scrollTo(childID, anchor: .top)
        }
    }
}
