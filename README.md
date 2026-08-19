# Precious Promises

A free SwiftUI iOS app of **Samuel Clark of St Albans (1684–1750)**, *A Collection of the Promises of Scripture* (also called *Precious Bible Promises* / Clarke's Scripture Promises).

There are **no ads, no tracking, no analytics, and no accounts**. Favorites are stored on the device only.

## Features

- **Browse** the original book tree: Parts → Chapters → Themes → verses
- **Search** Clark's heads, verse references, and King James wording
- **Star** favorites (SwiftData, on-device)
- Each verse shows **public-domain KJV** text in-app
- **Open in ESV** hands the reference to Safari or another app (`esv.org`, or bible.com translation id 59). ESV wording is never bundled, cached, or stored.

## Copyright and sources

| Work | Status in this app |
| --- | --- |
| Samuel Clark, *A Collection of the Promises of Scripture* (heads and references) | Public domain. Transcribed from the 1895 Cardiff edition: [Internet Archive](https://archive.org/details/collectionofprom00clar) |
| King James Version | Public domain. Bundled from [aruljohn/Bible-kjv](https://github.com/aruljohn/Bible-kjv) (1769/Blayney tradition) |
| ESV | © Crossway. **Not included.** “Open in ESV” opens another app or Safari |
| NASB / NIV / NET | **Not included** in any form |
| Tom Stewart, Historical Perspective (2009) | **Not included** |
| whatsaiththescripture.com | **Not used** (no scrape, no HTML copy) |

The 1895 book is **two parts plus an appendix** (blessings promised; duties to which promises are made; future state of the Church). That is Clark's own structure. The four-part split found on some modern sites is a later reformat and is not used here.

See [docs/CORPUS.md](docs/CORPUS.md) for how the catalog was extracted and how to proof remaining OCR.

## Build on a Mac

This repository is an Xcode iOS project. A Linux machine cannot run the iOS Simulator.

1. Install Xcode 15 or later (iOS 17 SDK).
2. Open `ClarkePromises/ClarkePromises.xcodeproj`.
3. Select an iPhone or iPad simulator, or your device.
4. Set your Development Team under the ClarkePromises target if you want to run on a device.
5. Press Run.

Bundle identifier: `com.athomas13727.ClarkePromises`  
Display name: **Precious Promises**  
Deployment target: **iOS 17+**

## Project layout

```
ClarkePromises/                 Xcode app (SwiftUI + SwiftData)
  ClarkePromises/Resources/clarke-promises.json
scripts/build_corpus.py         Rebuild heads + KJV pairing from the 1895 EPUB
scripts/validate_corpus.py
scripts/test_logic.py
docs/CORPUS.md
```

## Rebuild and check the catalog (any OS with Python 3)

```bash
python3 scripts/validate_corpus.py
python3 scripts/test_logic.py
```

Those checks confirm the Free Access theme, KJV-only verse wording, and ESV *link* shapes (URLs only; no ESV text).

To regenerate `clarke-promises.json` after proofing references, follow [docs/CORPUS.md](docs/CORPUS.md).

## Product

Prepared for Aaron Thomas. Free to use. No telemetry.
