import SwiftUI

struct AboutView: View {
    @Environment(CatalogStore.self) private var catalog

    var body: some View {
        List {
            Section("The compiler") {
                Text("Samuel Clark (also Clarke), 1684–1750, of St Albans, collected the promises of Scripture under their proper heads. The book is often called Precious Bible Promises or Clarke's Scripture Promises.")
                Text(catalog.meta.title)
                    .font(.headline)
                Text(catalog.meta.edition)
            }

            Section("This free app") {
                LabeledContent("Price") { Text("Free") }
                LabeledContent("Advertising") { Text("None") }
                LabeledContent("Tracking / analytics") { Text("None") }
                LabeledContent("Accounts") { Text("None") }
                Text("Favorites stay on this device (SwiftData). There is no sign-in and no network use except when you choose Open in ESV.")
            }

            Section("Texts and copyright") {
                Text("In-app Bible wording is the public-domain King James Version only.")
                Text(catalog.meta.kjvSource)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                Text("Clark's heads and the verse references were transcribed from the public-domain 1895 Internet Archive edition:")
                Link(catalog.meta.source, destination: URL(string: catalog.meta.source)!)
                Text("The English Standard Version is © Crossway. This app does not bundle, cache, or store ESV, NASB, NIV, or NET text. “Open in ESV” hands the reference to Safari or another Bible app.")
            }

            Section("What is not included") {
                ForEach(catalog.meta.excluded, id: \.self) { line in
                    Text(line)
                }
                Text("Isaac Watts's recommendation and Clark's introduction are omitted here so the app stays a promise reader, not a reprint of the whole front matter.")
            }

            Section("Corpus") {
                Text(catalog.meta.structure)
                LabeledContent("Themes") { Text("\(catalog.meta.themeCount)") }
                LabeledContent("Promise entries") { Text("\(catalog.meta.verseEntryCount)") }
                Text("Heads follow the original two parts plus appendix. The modern four-part rearrangement used on some websites is not used.")
                Text("References were recovered from the 1895 scan (EPUB/OCR) and then looked up in a public-domain KJV. A few OCR readings may still need proofing against the page images; see docs/CORPUS.md in the source repository.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Section("Product") {
                Text("Prepared for Aaron Thomas.")
                Text("No analytics SDKs are linked. The app makes no API calls of its own.")
            }
        }
        .navigationTitle("About")
    }
}
