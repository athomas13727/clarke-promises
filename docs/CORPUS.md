# Corpus notes

This app ships Clark's heads and verse *references* recovered from the
public-domain 1895 Cardiff edition on Internet Archive, then pairs each
reference with public-domain King James wording.

## Sources that were used

- Samuel Clark, *A Collection of the Promises of Scripture* (1895),
  [archive.org/details/collectionofprom00clar](https://archive.org/details/collectionofprom00clar).
  Heads and references come from the item EPUB (the plain `djvu.txt` file
  for this item stops around printed p. 124 and is incomplete).
- Public-domain KJV JSON from [aruljohn/Bible-kjv](https://github.com/aruljohn/Bible-kjv)
  (1769/Blayney tradition). Only verses cited by Clark are bundled.

## Sources that were not used

- whatsaiththescripture.com was not scraped or copied.
- Tom Stewart's 2009 Historical Perspective essay is not included.
- No ESV, NASB, NIV, or NET text is downloaded, cached, or stored.

## Book structure

The 1895 book is **two parts plus an appendix**, not the later four-part
website split:

1. **Part I** — The blessings promised to the good
   - Ch. 1 Temporal blessings
   - Ch. 2 Troubles of life
   - Ch. 3 Spiritual blessings in this life (includes *Free Access to God, with Acceptance*)
   - Ch. 4 Blessings in the other world
2. **Part II** — Promises to several graces and duties
   - Ch. 1 First table
   - Ch. 2 Second table
   - Ch. 3 Both tables
3. **Appendix** — State of the Church, then the conclusion that God will
   perform all his promises

Printed page *N* in that edition corresponds to EPUB `page_{N+90}.html`.

## How the extract was built

```bash
# 1. 1895 EPUB
curl -L -o /tmp/collectionofprom00clar.epub \
  https://archive.org/download/collectionofprom00clar/collectionofprom00clar.epub

# 2. Public-domain KJV books (see scripts/build_corpus.py BOOK_FILES)
#    Download the 66 JSON files from aruljohn/Bible-kjv into a directory.

# 3. Rebuild the bundled catalog
python3 scripts/build_corpus.py \
  --epub /tmp/collectionofprom00clar.epub \
  --kjv-dir /path/to/kjv-json \
  --out ClarkePromises/ClarkePromises/Resources/clarke-promises.json
```

`scripts/validate_corpus.py` checks schema, the required Free Access theme,
KJV-only wording, and that no modern-translation samples are present.

## How to finish / proof the corpus

The first ship is a **working extract of the whole tree** (every TOC head
that yielded at least one resolvable KJV verse). It is not a diplomatic
transcription of every line of the 272-page body.

To finish it:

1. Open the IA page images for a theme (use `sourcePage` in the JSON).
2. Compare Clark's printed references with the `displayRef` list.
3. Watch for OCR traps in this edition: long-s/`f` (`fob` = Job, `fohn` = John),
   roman `l` read as `1` (Ps. l. 15 = Psalm 50:15), and `cxiv`/`cxlv` swaps
   in the Psalms.
4. Add or correct references in `scripts/build_corpus.py` (prefer the
   `curated` list on a theme, or tighten the page range).
5. Rebuild and run `python3 scripts/validate_corpus.py`.
6. Do not paste ESV/NASB/NIV/NET wording into the JSON. Look the verse up
   in the KJV dataset only.

Watts's recommendation and Clark's introduction are intentionally omitted
from the app so it remains a promise reader.
