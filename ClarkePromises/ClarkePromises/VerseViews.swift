import SafariServices
import SwiftData
import SwiftUI

struct ReaderVerseBlock: View {
    let verse: CatalogVerse
    var themeID: String? = nil
    var emphasized: Bool = false

    @ScaledMetric(relativeTo: .body) private var verseSize: CGFloat = 19
    @ScaledMetric(relativeTo: .body) private var verseLine: CGFloat = 28
    @ScaledMetric(relativeTo: .footnote) private var citationSize: CGFloat = 13
    @ScaledMetric(relativeTo: .body) private var markSize: CGFloat = 17

    private let controlHit: CGFloat = 44

    @State private var showingTranslations = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(Self.displayKJV(verse.kjv))
                .font(AppAppearance.readerSerif(verseSize))
                .foregroundStyle(AppAppearance.ink)
                .lineSpacing(max(0, verseLine - verseSize))
                .fixedSize(horizontal: false, vertical: true)

            HStack(alignment: .center, spacing: 4) {
                Text(verse.displayRef)
                    .font(AppAppearance.citationSerif(citationSize))
                    .foregroundStyle(AppAppearance.inkSecondary)
                Spacer(minLength: 8)
                HStack(spacing: 10 - (controlHit - markSize)) {
                    FavoriteStarButton(verse: verse, themeID: themeID, pointSize: markSize)
                    otherTranslationsButton
                }
            }
            .padding(.top, 10)
        }
        .padding(.horizontal, emphasized ? 8 : 0)
        .background {
            if emphasized {
                AppAppearance.highlight
                    .padding(.horizontal, -8)
            }
        }
        .sheet(isPresented: $showingTranslations) {
            OtherTranslationsSheet(verse: verse)
                .presentationDetents([.medium])
                .presentationBackground(AppAppearance.parchment)
        }
    }

    private var otherTranslationsButton: some View {
        Button {
            showingTranslations = true
        } label: {
            Image(systemName: "link")
                .font(AppAppearance.uiSans(markSize, weight: .regular))
                .foregroundStyle(AppAppearance.inkSecondary)
                .frame(width: controlHit, height: controlHit)
                .contentShape(Rectangle())
        }
        .buttonStyle(CitationControlPressStyle())
        .accessibilityLabel("Other translations")
    }

    /// Running KJV only: no wrapping quotes, no leading in-text verse numbers.
    static func displayKJV(_ text: String) -> String {
        var t = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let wraps = CharacterSet(charactersIn: "\"“”‘’")
        while let scalar = t.unicodeScalars.first, wraps.contains(scalar) {
            t.removeFirst()
            t = t.trimmingCharacters(in: .whitespaces)
        }
        while let scalar = t.unicodeScalars.last, wraps.contains(scalar) {
            t.removeLast()
            t = t.trimmingCharacters(in: .whitespaces)
        }
        if let match = t.range(of: #"^\d+[.)]?\s+"#, options: .regularExpression) {
            t.removeSubrange(match)
        }
        return t.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

struct SearchHitRow: View {
    let hit: SearchHit

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(hit.theme.title)
                .font(AppAppearance.uiSans(12, weight: .medium))
                .foregroundStyle(AppAppearance.inkSecondary)
            Text(ReaderVerseBlock.displayKJV(hit.verse.kjv))
                .font(AppAppearance.readerSerif(16))
                .foregroundStyle(AppAppearance.ink)
                .lineLimit(3)
            Text(hit.verse.displayRef)
                .font(AppAppearance.uiSans(11))
                .foregroundStyle(AppAppearance.inkSecondary)
        }
        .padding(.vertical, 4)
    }
}

struct FavoriteStarButton: View {
    let verse: CatalogVerse
    var themeID: String? = nil
    var pointSize: CGFloat = 17
    @Environment(\.modelContext) private var modelContext
    @Query private var favorites: [FavoriteVerse]

    var body: some View {
        Button {
            FavoritesStore.toggle(
                verse: verse,
                themeID: themeID,
                favorites: favorites,
                context: modelContext
            )
        } label: {
            Image(systemName: isFavorite ? "star.fill" : "star")
                .font(AppAppearance.uiSans(pointSize))
                .foregroundStyle(isFavorite ? AppAppearance.accent : AppAppearance.inkSecondary)
                .frame(width: 44, height: 44)
                .contentShape(Rectangle())
                .accessibilityLabel(isFavorite ? "Remove favorite" : "Add favorite")
        }
        .buttonStyle(.plain)
    }

    private var isFavorite: Bool {
        FavoritesStore.isFavorite(verse.osis, in: favorites)
    }
}

/// Finger-down wash on the 44pt hit, same token as the TOC wash.
private struct CitationControlPressStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .background {
                AppAppearance.highlight
                    .opacity(configuration.isPressed ? 1 : 0)
            }
            .animation(nil, value: configuration.isPressed)
    }
}

private struct OtherTranslationsSheet: View {
    let verse: CatalogVerse
    @State private var safariPage: SafariPage?

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("Other translations")
                .font(AppAppearance.uiSans(13))
                .foregroundStyle(AppAppearance.inkSecondary)
                .frame(maxWidth: .infinity)
                .padding(.top, 20)
                .padding(.bottom, 16)

            ForEach(BibleGatewayVersion.allCases) { version in
                Button {
                    safariPage = SafariPage(url: ESVLink.bibleGatewayURL(for: verse, version: version))
                } label: {
                    HStack(spacing: 12) {
                        Text(version.rawValue)
                            .font(AppAppearance.uiSans(17))
                            .foregroundStyle(AppAppearance.ink)
                        Spacer(minLength: 8)
                        Image(systemName: "arrow.up.right")
                            .font(AppAppearance.uiSans(13, weight: .medium))
                            .foregroundStyle(AppAppearance.inkSecondary)
                    }
                    .padding(.horizontal, 22)
                    .padding(.vertical, 14)
                    .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                    .contentShape(Rectangle())
                }
                .buttonStyle(CitationControlPressStyle())

                if version != .niv {
                    AppAppearance.hairline
                        .frame(height: 1)
                }
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .background(AppAppearance.parchment)
        .sheet(item: $safariPage) { page in
            SafariView(url: page.url)
                .ignoresSafeArea()
        }
    }
}

private struct SafariPage: Identifiable {
    let url: URL
    var id: String { url.absoluteString }
}

private struct SafariView: UIViewControllerRepresentable {
    let url: URL

    func makeUIViewController(context: Context) -> SFSafariViewController {
        SFSafariViewController(url: url)
    }

    func updateUIViewController(_ controller: SFSafariViewController, context: Context) {}
}
