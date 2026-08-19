import SwiftUI

struct BrowseView: View {
    @Environment(CatalogStore.self) private var catalog
    @State private var expandedChapterID = "p1-c1"
    @State private var showingAbout = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 48) {
                ForEach(catalog.parts) { part in
                    TOCPartSection(part: part, expandedChapterID: $expandedChapterID)
                }

                Button {
                    showingAbout = true
                } label: {
                    Text("About this book")
                        .font(AppAppearance.displaySerif(15))
                        .foregroundStyle(AppAppearance.inkSecondary)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
                .padding(.top, 8)
                .accessibilityLabel("About this book")
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
    @Binding var expandedChapterID: String

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            Text(partLabel)
                .font(AppAppearance.uiSans(11, weight: .semibold))
                .tracking(2.4)
                .foregroundStyle(AppAppearance.inkSecondary)
                .frame(maxWidth: .infinity)

            ForEach(part.chapters) { chapter in
                TOCChapterSection(chapter: chapter, expandedChapterID: $expandedChapterID)
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
    @Binding var expandedChapterID: String

    private var expanded: Bool {
        expandedChapterID == chapter.id
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
                    if !expanded {
                        expandedChapterID = chapter.id
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
                .accessibilityHint(expanded ? "This chapter is open" : "Expands this chapter and closes the open chapter")
            }

            if expanded {
                VStack(alignment: .leading, spacing: 0) {
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
        VStack(alignment: .leading, spacing: 0) {
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
                            .foregroundStyle(AppAppearance.ink)
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.leading, numberColumn + titleGutter + CGFloat(indent) * childIndent)
                    }
                }
                .padding(.vertical, 8)
                .frame(minHeight: 44, alignment: .center)
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(Rectangle())
            }
            .buttonStyle(TOCPressStyle())

            ForEach(theme.children) { child in
                // AnyView breaks the `some View` cycle at the only recursive TOC edge.
                AnyView(TOCThemeNode(theme: child, indent: indent + 1))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// Finger-down wash only. Outer TOC is 36pt; wash sits at 22pt from the screen edge.
private struct TOCPressStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .background {
                AppAppearance.highlight
                    .padding(.horizontal, -14)
                    .opacity(configuration.isPressed ? 1 : 0)
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
                Text("Theme missing")
                    .font(AppAppearance.displaySerif(17))
                    .foregroundStyle(AppAppearance.inkSecondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .readerChrome()
            }
        }
    }
}

private struct ThemeReader: View {
    let theme: CatalogTheme
    let route: ThemeRoute
    @Environment(CatalogStore.self) private var catalog

    @ScaledMetric(relativeTo: .caption2) private var chapterSize: CGFloat = 11
    @ScaledMetric(relativeTo: .title2) private var titleSize: CGFloat = 22
    /// Scale with body, not caption — caption-relative serif was resolving as SF.
    @ScaledMetric(relativeTo: .body) private var subheadSize: CGFloat = 12

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    chapterCue

                    titleBlock
                        .padding(.top, 6)

                    if !theme.verses.isEmpty {
                        verseStack(theme.verses)
                            .padding(.top, 22)
                    }

                    ForEach(Array(theme.children.enumerated()), id: \.element.id) { index, child in
                        let beforeSubhead: CGFloat = (!theme.verses.isEmpty || index > 0) ? 32 : 22
                        childGroup(child)
                            .padding(.top, beforeSubhead)
                    }
                }
                .padding(.horizontal, 22)
                .padding(.top, 8)
                .padding(.bottom, 40)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .scrollIndicators(.automatic)
            .onAppear {
                scroll(using: proxy)
            }
        }
        .readerChrome()
        .background(FlattenSystemBackChrome())
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
    }

    @ViewBuilder
    private var chapterCue: some View {
        if let (_, chapter) = catalog.placement(of: theme) {
            Text("Chapter \(chapter.number)")
                .font(AppAppearance.uiSans(chapterSize))
                .foregroundStyle(AppAppearance.inkSecondary)
        }
    }

    private var titleBlock: some View {
        Text(pageTitle)
            .font(AppAppearance.displaySerif(titleSize, weight: .semibold))
            .foregroundStyle(AppAppearance.ink)
            .multilineTextAlignment(.leading)
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var pageTitle: String {
        if let number = theme.number {
            return "\(number). \(theme.title)"
        }
        return theme.title
    }

    private func childGroup(_ child: CatalogTheme) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            subhead(child.title)
                .id(child.id)

            if !child.verses.isEmpty {
                verseStack(child.verses)
                    .padding(.top, 12)
            }

            ForEach(Array(child.children.enumerated()), id: \.element.id) { index, grand in
                subhead(grand.title)
                    .id(grand.id)
                    .padding(.top, index == 0 && child.verses.isEmpty ? 12 : 32)

                if !grand.verses.isEmpty {
                    verseStack(grand.verses)
                        .padding(.top, 12)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func subhead(_ title: String) -> some View {
        // AttributedString + UIFont New York avoids SwiftUI `.tracking` / caption
        // `Font.system(design: .serif)` falling back to SF at 12pt.
        Text(serifSubheadText(title.uppercased()))
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func serifSubheadText(_ title: String) -> AttributedString {
        var attributes = AttributeContainer()
        attributes.font = AppAppearance.newYork(subheadSize, weight: .semibold)
        attributes.kern = 1
        attributes.foregroundColor = AppAppearance.inkSecondary
        return AttributedString(title, attributes: attributes)
    }

    private func verseStack(_ verses: [CatalogVerse]) -> some View {
        VStack(alignment: .leading, spacing: 24) {
            ForEach(verses) { verse in
                ReaderVerseBlock(
                    verse: verse,
                    themeID: theme.id,
                    emphasized: verse.id == route.highlightVerseID
                )
                .id(verse.id)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func scroll(using proxy: ScrollViewProxy) {
        if let verseID = route.highlightVerseID {
            proxy.scrollTo(verseID, anchor: .center)
        } else if let childID = route.highlightChildID {
            proxy.scrollTo(childID, anchor: .top)
        }
    }
}
