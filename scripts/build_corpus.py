#!/usr/bin/env python3
"""Build the bundled Clarke catalog + public-domain KJV texts.

Heads and verse *references* come from the 1895 Internet Archive edition
(https://archive.org/details/collectionofprom00clar). Verse *wording* is
looked up in a public-domain KJV dataset (aruljohn/Bible-kjv).

This script does not scrape whatsaiththescripture.com and does not include
modern essays.

Usage:
  python3 scripts/build_corpus.py \\
      --epub /tmp/ia-clark/book.epub \\
      --kjv-dir /tmp/kjv-books \\
      --out ClarkePromises/ClarkePromises/Resources/clarke-promises.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import OrderedDict
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme_tree import CHAPTERS, PARTS, TREES, Node

BOOK_FILES = {
    "Genesis": "Genesis.json",
    "Exodus": "Exodus.json",
    "Leviticus": "Leviticus.json",
    "Numbers": "Numbers.json",
    "Deuteronomy": "Deuteronomy.json",
    "Joshua": "Joshua.json",
    "Judges": "Judges.json",
    "Ruth": "Ruth.json",
    "1 Samuel": "1Samuel.json",
    "2 Samuel": "2Samuel.json",
    "1 Kings": "1Kings.json",
    "2 Kings": "2Kings.json",
    "1 Chronicles": "1Chronicles.json",
    "2 Chronicles": "2Chronicles.json",
    "Ezra": "Ezra.json",
    "Nehemiah": "Nehemiah.json",
    "Esther": "Esther.json",
    "Job": "Job.json",
    "Psalms": "Psalms.json",
    "Proverbs": "Proverbs.json",
    "Ecclesiastes": "Ecclesiastes.json",
    "Song of Solomon": "SongofSolomon.json",
    "Isaiah": "Isaiah.json",
    "Jeremiah": "Jeremiah.json",
    "Lamentations": "Lamentations.json",
    "Ezekiel": "Ezekiel.json",
    "Daniel": "Daniel.json",
    "Hosea": "Hosea.json",
    "Joel": "Joel.json",
    "Amos": "Amos.json",
    "Obadiah": "Obadiah.json",
    "Jonah": "Jonah.json",
    "Micah": "Micah.json",
    "Nahum": "Nahum.json",
    "Habakkuk": "Habakkuk.json",
    "Zephaniah": "Zephaniah.json",
    "Haggai": "Haggai.json",
    "Zechariah": "Zechariah.json",
    "Malachi": "Malachi.json",
    "Matthew": "Matthew.json",
    "Mark": "Mark.json",
    "Luke": "Luke.json",
    "John": "John.json",
    "Acts": "Acts.json",
    "Romans": "Romans.json",
    "1 Corinthians": "1Corinthians.json",
    "2 Corinthians": "2Corinthians.json",
    "Galatians": "Galatians.json",
    "Ephesians": "Ephesians.json",
    "Philippians": "Philippians.json",
    "Colossians": "Colossians.json",
    "1 Thessalonians": "1Thessalonians.json",
    "2 Thessalonians": "2Thessalonians.json",
    "1 Timothy": "1Timothy.json",
    "2 Timothy": "2Timothy.json",
    "Titus": "Titus.json",
    "Philemon": "Philemon.json",
    "Hebrews": "Hebrews.json",
    "James": "James.json",
    "1 Peter": "1Peter.json",
    "2 Peter": "2Peter.json",
    "1 John": "1John.json",
    "2 John": "2John.json",
    "3 John": "3John.json",
    "Jude": "Jude.json",
    "Revelation": "Revelation.json",
}

OSIS = {
    "Genesis": "Gen",
    "Exodus": "Exod",
    "Leviticus": "Lev",
    "Numbers": "Num",
    "Deuteronomy": "Deut",
    "Joshua": "Josh",
    "Judges": "Judg",
    "Ruth": "Ruth",
    "1 Samuel": "1Sam",
    "2 Samuel": "2Sam",
    "1 Kings": "1Kgs",
    "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr",
    "2 Chronicles": "2Chr",
    "Ezra": "Ezra",
    "Nehemiah": "Neh",
    "Esther": "Esth",
    "Job": "Job",
    "Psalms": "Ps",
    "Proverbs": "Prov",
    "Ecclesiastes": "Eccl",
    "Song of Solomon": "Song",
    "Isaiah": "Isa",
    "Jeremiah": "Jer",
    "Lamentations": "Lam",
    "Ezekiel": "Ezek",
    "Daniel": "Dan",
    "Hosea": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Obad",
    "Jonah": "Jonah",
    "Micah": "Mic",
    "Nahum": "Nah",
    "Habakkuk": "Hab",
    "Zephaniah": "Zeph",
    "Haggai": "Hag",
    "Zechariah": "Zech",
    "Malachi": "Mal",
    "Matthew": "Matt",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Romans": "Rom",
    "1 Corinthians": "1Cor",
    "2 Corinthians": "2Cor",
    "Galatians": "Gal",
    "Ephesians": "Eph",
    "Philippians": "Phil",
    "Colossians": "Col",
    "1 Thessalonians": "1Thess",
    "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim",
    "2 Timothy": "2Tim",
    "Titus": "Titus",
    "Philemon": "Phlm",
    "Hebrews": "Heb",
    "James": "Jas",
    "1 Peter": "1Pet",
    "2 Peter": "2Pet",
    "1 John": "1John",
    "2 John": "2John",
    "3 John": "3John",
    "Jude": "Jude",
    "Revelation": "Rev",
}

DISPLAY_BOOK = {
    "Psalms": "Psalm",
    "Song of Solomon": "Song of Solomon",
}

# Ordered longest-first so "1 Cor" wins over "Cor".
BOOK_ABBREVS = [
    ("1 chronicles", "1 Chronicles"),
    ("2 chronicles", "2 Chronicles"),
    ("1 corinthians", "1 Corinthians"),
    ("2 corinthians", "2 Corinthians"),
    ("1 thessalonians", "1 Thessalonians"),
    ("2 thessalonians", "2 Thessalonians"),
    ("1 timothy", "1 Timothy"),
    ("2 timothy", "2 Timothy"),
    ("1 samuel", "1 Samuel"),
    ("2 samuel", "2 Samuel"),
    ("1 kings", "1 Kings"),
    ("2 kings", "2 Kings"),
    ("1 peter", "1 Peter"),
    ("2 peter", "2 Peter"),
    ("1 john", "1 John"),
    ("2 john", "2 John"),
    ("3 john", "3 John"),
    ("song of solomon", "Song of Solomon"),
    ("song of songs", "Song of Solomon"),
    ("canticles", "Song of Solomon"),
    ("deuteronomy", "Deuteronomy"),
    ("ecclesiastes", "Ecclesiastes"),
    ("lamentations", "Lamentations"),
    ("revelation", "Revelation"),
    ("philippians", "Philippians"),
    ("colossians", "Colossians"),
    ("thessalonians", "1 Thessalonians"),
    ("zechariah", "Zechariah"),
    ("zephaniah", "Zephaniah"),
    ("habakkuk", "Habakkuk"),
    ("malachi", "Malachi"),
    ("matthew", "Matthew"),
    ("genesis", "Genesis"),
    ("exodus", "Exodus"),
    ("leviticus", "Leviticus"),
    ("numbers", "Numbers"),
    ("joshua", "Joshua"),
    ("judges", "Judges"),
    ("esther", "Esther"),
    ("psalms", "Psalms"),
    ("proverbs", "Proverbs"),
    ("isaiah", "Isaiah"),
    ("jeremiah", "Jeremiah"),
    ("ezekiel", "Ezekiel"),
    ("daniel", "Daniel"),
    ("hosea", "Hosea"),
    ("amos", "Amos"),
    ("obadiah", "Obadiah"),
    ("jonah", "Jonah"),
    ("micah", "Micah"),
    ("nahum", "Nahum"),
    ("haggai", "Haggai"),
    ("romans", "Romans"),
    ("galatians", "Galatians"),
    ("ephesians", "Ephesians"),
    ("hebrews", "Hebrews"),
    ("james", "James"),
    ("philemon", "Philemon"),
    ("chronicles", "1 Chronicles"),
    ("corinthians", "1 Corinthians"),
    ("thess", "1 Thessalonians"),
    ("timothy", "1 Timothy"),
    ("samuel", "1 Samuel"),
    ("kings", "1 Kings"),
    ("peter", "1 Peter"),
    ("nehemiah", "Nehemiah"),
    ("1 chron", "1 Chronicles"),
    ("2 chron", "2 Chronicles"),
    ("1 chr", "1 Chronicles"),
    ("2 chr", "2 Chronicles"),
    ("1 cor", "1 Corinthians"),
    ("2 cor", "2 Corinthians"),
    ("1 thes", "1 Thessalonians"),
    ("2 thes", "2 Thessalonians"),
    ("1 thess", "1 Thessalonians"),
    ("2 thess", "2 Thessalonians"),
    ("1 tim", "1 Timothy"),
    ("2 tim", "2 Timothy"),
    ("1 sam", "1 Samuel"),
    ("2 sam", "2 Samuel"),
    ("1 kgs", "1 Kings"),
    ("2 kgs", "2 Kings"),
    ("1 kin", "1 Kings"),
    ("2 kin", "2 Kings"),
    ("1 pet", "1 Peter"),
    ("2 pet", "2 Peter"),
    ("i chron", "1 Chronicles"),
    ("ii chron", "2 Chronicles"),
    ("i cor", "1 Corinthians"),
    ("ii cor", "2 Corinthians"),
    ("i thes", "1 Thessalonians"),
    ("ii thes", "2 Thessalonians"),
    ("i tim", "1 Timothy"),
    ("ii tim", "2 Timothy"),
    ("i sam", "1 Samuel"),
    ("ii sam", "2 Samuel"),
    ("i pet", "1 Peter"),
    ("ii pet", "2 Peter"),
    ("i john", "1 John"),
    ("ii john", "2 John"),
    ("iii john", "3 John"),
    ("1 jn", "1 John"),
    ("2 jn", "2 John"),
    ("3 jn", "3 John"),
    ("deut", "Deuteronomy"),
    ("eccl", "Ecclesiastes"),
    ("eccles", "Ecclesiastes"),
    ("lam", "Lamentations"),
    ("rev", "Revelation"),
    ("phil", "Philippians"),
    ("col", "Colossians"),
    ("zech", "Zechariah"),
    ("zeph", "Zephaniah"),
    ("hab", "Habakkuk"),
    ("mal", "Malachi"),
    ("matt", "Matthew"),
    ("mat", "Matthew"),
    ("gen", "Genesis"),
    ("exod", "Exodus"),
    ("ex", "Exodus"),
    ("lev", "Leviticus"),
    ("num", "Numbers"),
    ("numb", "Numbers"),
    ("josh", "Joshua"),
    ("judg", "Judges"),
    ("esth", "Esther"),
    ("psal", "Psalms"),
    ("psa", "Psalms"),
    ("ps", "Psalms"),
    ("sal", "Psalms"),
    ("prov", "Proverbs"),
    ("pro", "Proverbs"),
    ("isa", "Isaiah"),
    ("is", "Isaiah"),
    ("jer", "Jeremiah"),
    ("ezek", "Ezekiel"),
    ("eze", "Ezekiel"),
    ("dan", "Daniel"),
    ("hos", "Hosea"),
    ("has", "Hosea"),
    ("joel", "Joel"),
    ("amos", "Amos"),
    ("obad", "Obadiah"),
    ("jon", "Jonah"),
    ("mic", "Micah"),
    ("nah", "Nahum"),
    ("hag", "Haggai"),
    ("rom", "Romans"),
    ("gal", "Galatians"),
    ("eph", "Ephesians"),
    ("heb", "Hebrews"),
    ("jas", "James"),
    ("phlm", "Philemon"),
    ("job", "Job"),
    ("fob", "Job"),
    ("iob", "Job"),
    ("ezr", "Ezra"),
    ("neh", "Nehemiah"),
    ("ruth", "Ruth"),
    ("mark", "Mark"),
    ("luke", "Luke"),
    ("john", "John"),
    ("fohn", "John"),
    ("iohn", "John"),
    ("acts", "Acts"),
    ("act", "Acts"),
    ("tit", "Titus"),
    ("jude", "Jude"),
    ("saiah", "Isaiah"),
]


def roman_to_int(token: str) -> int | None:
    token = token.lower().replace(" ", "")
    if not token or not re.fullmatch(r"[ivxlcdm]+", token):
        return None
    values = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    total = 0
    prev = 0
    for ch in reversed(token):
        val = values[ch]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total if 1 <= total <= 150 else None


def ocr_chapter_candidates(raw: str) -> list[int]:
    raw = raw.strip()
    raw = raw.replace("lo", "10").replace("l0", "10")
    collapsed = re.sub(r"\s+", "", raw)
    # Common OCR: "1 2" => 12, "2 1" => 21
    if re.fullmatch(r"\d[\s.]+\d", raw):
        digits = re.sub(r"\D", "", raw)
        if digits:
            collapsed = digits
    candidates: list[int] = []

    def add(n: int | None) -> None:
        if n and 1 <= n <= 150 and n not in candidates:
            candidates.append(n)

    if re.fullmatch(r"\d{1,3}", collapsed):
        add(int(collapsed))

    # Ixxxiv / Iviii / Ixv are almost always lxxxiv / lviii / lxv (OCR I for l).
    # Prefer the l-reading first so Is. Ixv. 13 is Isaiah 65:13, not 14:13.
    roman = collapsed.lower().replace("j", "i")
    if roman.startswith("i") and len(roman) >= 3 and roman[1] in "xvl":
        add(roman_to_int("l" + roman[1:]))
    add(roman_to_int(roman))
    if roman.startswith("x") and "u" not in roman:
        # x^v'm style garbage is ignored by roman_to_int
        add(roman_to_int(roman.replace("^", "").replace("'", "")))
    return candidates


def ocr_verse_candidates(raw: str) -> list[int]:
    raw = raw.strip().replace("lo", "10")
    collapsed = re.sub(r"\s+", "", raw)
    candidates: list[int] = []

    def add(n: int | None) -> None:
        if n and 1 <= n <= 176 and n not in candidates:
            candidates.append(n)

    # "Ver. 1 3" / "1 2" => 13 / 12
    spaced = re.sub(r"\s+", "", raw)
    if re.fullmatch(r"\d{1,3}", spaced):
        add(int(spaced))
        return candidates
    if re.fullmatch(r"\d{1,3}", collapsed):
        add(int(collapsed))
        return candidates
    low = collapsed.lower()
    # II / ll as 11 (Prov. ix. II = 9:11), then roman 2
    if low in {"ii", "ll", "il", "li"}:
        add(11)
    # 1 Pet. iii. v2i = 3:13; Prov. i. 2)2i = 1:33
    if low in {"v2i", "vzi"}:
        add(13)
    if re.sub(r"[^0-9a-z]+", "", low) in {"22i", "2i2", "232"}:
        add(33)
    add(roman_to_int(low))
    if low.startswith("i") and len(low) >= 3:
        add(roman_to_int("l" + low[1:]))
    digits = re.sub(r"\D", "", raw)
    if digits:
        add(int(digits))
    return candidates


def load_kjv(kjv_dir: Path) -> dict[tuple[str, int, int], str]:
    lookup: dict[tuple[str, int, int], str] = {}
    for book, filename in BOOK_FILES.items():
        data = json.loads((kjv_dir / filename).read_text(encoding="utf-8"))
        for chapter in data["chapters"]:
            ch = int(chapter["chapter"])
            for verse in chapter["verses"]:
                lookup[(book, ch, int(verse["verse"]))] = verse["text"].strip()
    return lookup


def extract_epub_pages(epub_path: Path) -> dict[int, str]:
    pages: dict[int, str] = {}
    with zipfile.ZipFile(epub_path) as zf:
        names = [n for n in zf.namelist() if re.fullmatch(r"EPUB/page_\d+\.html", n)]
        for name in names:
            n = int(re.search(r"(\d+)", Path(name).stem).group(1))
            raw = zf.read(name).decode("utf-8", "replace")
            raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
            raw = re.sub(r"</p>", "\n", raw, flags=re.I)
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = unescape(raw)
            raw = re.sub(r"[ \t]+", " ", raw)
            pages[n] = raw
    return pages


def printed_to_epub(printed: int) -> int:
    return printed + 90


def pages_text(pages: dict[int, str], start: int, end: int) -> str:
    chunks = []
    for printed in range(start, max(start, end)):
        epub = printed_to_epub(printed)
        if epub in pages:
            chunks.append(pages[epub])
    return "\n".join(chunks)


def slice_text(text: str, start_marker: str | None, end_marker: str | None) -> str:
    if start_marker:
        idx = text.lower().find(start_marker.lower())
        if idx >= 0:
            text = text[idx:]
    if end_marker:
        idx = text.lower().find(end_marker.lower())
        if idx > 20:
            text = text[:idx]
    return text


def normalize_for_refs(text: str) -> str:
    text = text.replace("[ohn", "John").replace("[ohn", "John")
    text = text.replace("fohn", "John").replace("fob", "Job").replace("iob", "Job")
    text = text.replace("Tivi.", "Tim.").replace("Tivi ", "Tim ")
    text = re.sub(r"/ \s*Sam\.", "1 Sam.", text)
    text = text.replace("SAIAH", "Isaiah").replace("SAL.", "Psal.")
    text = text.replace("PSAL.", "Psal.").replace("EUT.", "Deut.")
    text = text.replace("Ninnb.", "Numb.").replace("Ro}n.", "Rom.")
    text = re.sub(r"\bI\s+(Cor|Pet|John|Thes|Tim|Sam|Kin|Chr)\b", r"1 \1", text)
    text = re.sub(r"\bII\s+(Cor|Pet|John|Thes|Tim|Sam|Kin|Chr)\b", r"2 \1", text)
    return text


def find_book_at(text: str, index: int) -> tuple[str, int] | None:
    window = text[max(0, index - 28) : index].lower()
    window = re.sub(r"[^a-z0-9 ]+", " ", window)
    window = re.sub(r"\s+", " ", window).strip()
    for abbr, book in BOOK_ABBREVS:
        if window.endswith(abbr) or window.endswith(" " + abbr):
            return book, len(abbr)
        # allow trailing punctuation already stripped
        if re.search(rf"(?:^| ){re.escape(abbr)}$", window):
            return book, len(abbr)
    return None


REF_RE = re.compile(
    r"""
    (?P<book>(?:[123]|I{1,3}|i{1,3})\s+)?
    (?P<name>[A-Za-z\[\]]{2,12})[.,]
    \s+
    (?P<chap>[ivxlcdmIVXLCDM0-9][ivxlcdmIVXLCDM0-9\s]{0,10})
    [.,]
    \s*
    (?P<verse>[ivxlcdmIVXLCDM0-9][ivxlcdmIVXLCDM0-9\s]{0,6})
    """,
    re.VERBOSE,
)

VER_RE = re.compile(
    r"""
    \bVer(?:se)?\.?\s*
    (?P<verse>[ivxlcdmIVXLCDM0-9][ivxlcdmIVXLCDM0-9\s]{0,6})
    """,
    re.VERBOSE | re.I,
)


def parse_refs(text: str, kjv: dict[tuple[str, int, int], str]) -> list[tuple[str, int, int]]:
    text = normalize_for_refs(text)
    found: list[tuple[str, int, int]] = []
    seen: set[tuple[str, int, int]] = set()
    last: tuple[str, int] | None = None

    def accept(book: str, chapter: int, verse: int) -> None:
        key = (book, chapter, verse)
        if key in kjv and key not in seen:
            seen.add(key)
            found.append(key)

    def try_lookup(book: str, chapters: list[int], verses: list[int]) -> bool:
        for ch in chapters:
            for vs in verses:
                if (book, ch, vs) in kjv:
                    accept(book, ch, vs)
                    return True
        # Psalm OCR: "Ps. 1. 15" is often Ps. l. 15 (50); cxiv/cxlv swaps
        if book == "Psalms":
            extras = []
            for ch in chapters:
                if ch == 1:
                    extras.append(50)
                if ch == 114:
                    extras.append(145)
                if ch == 145:
                    extras.append(114)
            for ch in extras:
                for vs in verses:
                    if (book, ch, vs) in kjv:
                        accept(book, ch, vs)
                        return True
        # Clark/OCR: "Ex. xxxiv. 25/28" is Ezekiel 34 (covenant of peace), not Exodus 34
        if book == "Exodus":
            for ch in chapters:
                if ch == 34:
                    for vs in verses:
                        if vs in {25, 28} and ("Ezekiel", ch, vs) in kjv:
                            accept("Ezekiel", ch, vs)
                            return True
        return False

    tokens: list[tuple[int, str, re.Match[str]]] = []
    for m in REF_RE.finditer(text):
        tokens.append((m.start(), "ref", m))
    for m in VER_RE.finditer(text):
        tokens.append((m.start(), "ver", m))
    tokens.sort(key=lambda item: item[0])

    for _, kind, m in tokens:
        if kind == "ver":
            if not last:
                continue
            verses = ocr_verse_candidates(m.group("verse"))
            try_lookup(last[0], [last[1]], verses)
            continue

        name = (m.group("name") or "").lower()
        prefix = (m.group("book") or "").strip().lower()
        probe = f"{prefix} {name}".strip()
        book = None
        for abbr, mapped in BOOK_ABBREVS:
            if probe == abbr or probe.replace(" ", "") == abbr.replace(" ", ""):
                book = mapped
                break
            if name == abbr or name.rstrip(".") == abbr:
                # numbered books need the prefix
                if mapped.startswith(("1 ", "2 ", "3 ")) and not prefix:
                    # "Pet." after "I Pet." already handled; bare Pet. => 1 Peter is OK
                    book = mapped
                elif not mapped.startswith(("1 ", "2 ", "3 ")):
                    book = mapped
                break
        if book is None:
            # reconstruct from surrounding text
            hit = find_book_at(text, m.start(2) if m.lastindex else m.start())
            if hit:
                book = hit[0]
        if book is None:
            # try name only
            for abbr, mapped in BOOK_ABBREVS:
                if name == abbr:
                    book = mapped
                    break
        if book is None:
            continue
        chapters = ocr_chapter_candidates(m.group("chap"))
        verses = ocr_verse_candidates(m.group("verse"))
        if try_lookup(book, chapters, verses):
            last = found[-1][:2]
            # additional verses listed as "21, 22"
            tail = text[m.end() : m.end() + 12]
            extra = re.match(r"\s*[,;]\s*(\d{1,3})", tail)
            if extra and last:
                try_lookup(book, [last[1]], [int(extra.group(1))])
    return found


def display_ref(book: str, chapter: int, verse: int, end_verse: int | None = None) -> str:
    title = DISPLAY_BOOK.get(book, book)
    if end_verse and end_verse != verse:
        return f"{title} {chapter}:{verse}–{end_verse}"
    return f"{title} {chapter}:{verse}"


def osis_id(book: str, chapter: int, verse: int, end_verse: int | None = None) -> str:
    base = f"{OSIS[book]}.{chapter}.{verse}"
    if end_verse and end_verse != verse:
        return f"{base}-{end_verse}"
    return base


def group_consecutive(refs: list[tuple[str, int, int]]) -> list[tuple[str, int, int, int]]:
    if not refs:
        return []
    grouped: list[tuple[str, int, int, int]] = []
    book, ch, start = refs[0]
    end = start
    for nxt in refs[1:]:
        if nxt[0] == book and nxt[1] == ch and nxt[2] == end + 1:
            end = nxt[2]
        else:
            grouped.append((book, ch, start, end))
            book, ch, start = nxt
            end = start
    grouped.append((book, ch, start, end))
    return grouped


def build_verse(
    theme_id: str,
    book: str,
    chapter: int,
    start: int,
    end: int,
    kjv: dict[tuple[str, int, int], str],
) -> dict:
    texts = [kjv[(book, chapter, v)] for v in range(start, end + 1)]
    return {
        "id": f"{theme_id}:{osis_id(book, chapter, start, end if end != start else None)}",
        "osis": osis_id(book, chapter, start, end if end != start else None),
        "displayRef": display_ref(book, chapter, start, end if end != start else None),
        "book": book,
        "chapter": chapter,
        "verse": start,
        "endVerse": end if end != start else None,
        "kjv": " ".join(texts),
    }


def collect_ref_keys(theme: dict) -> set[tuple[str, int, int]]:
    keys: set[tuple[str, int, int]] = set()
    for verse in theme.get("verses") or []:
        book = verse["book"]
        chapter = verse["chapter"]
        start = verse["verse"]
        end = verse.get("endVerse") or start
        for n in range(start, end + 1):
            keys.add((book, chapter, n))
    for child in theme.get("children") or []:
        keys |= collect_ref_keys(child)
    return keys


def count_nodes(theme: dict) -> int:
    return 1 + sum(count_nodes(child) for child in theme.get("children") or [])


def count_verses(theme: dict) -> int:
    total = len(theme.get("verses") or [])
    for child in theme.get("children") or []:
        total += count_verses(child)
    return total


def node_has_content(theme: dict) -> bool:
    if theme.get("verses"):
        return True
    return any(node_has_content(child) for child in theme.get("children") or [])


def prune_empty(theme: dict) -> dict | None:
    children = [c for child in theme.get("children") or [] if (c := prune_empty(child))]
    verses = theme.get("verses") or []
    if not verses and not children:
        return None
    out = dict(theme)
    if verses:
        out["verses"] = verses
    else:
        out.pop("verses", None)
    if children:
        out["children"] = children
    else:
        out.pop("children", None)
    return out


def build_node(node: Node, pages: dict[int, str], kjv: dict, report_lines: list[str]) -> dict:
    text = slice_text(pages_text(pages, node.start, node.end), node.start_marker, node.end_marker)
    refs = parse_refs(text, kjv)
    if node.exclude:
        refs = [ref for ref in refs if ref not in node.exclude]
    if node.curated:
        for item in node.curated:
            if item not in refs:
                refs.append(item)
    children = [build_node(child, pages, kjv, report_lines) for child in node.children]
    claimed: set[tuple[str, int, int]] = set()
    for child in children:
        claimed |= collect_ref_keys(child)
    if children:
        refs = [ref for ref in refs if ref not in claimed]
    uniq = list(OrderedDict.fromkeys(refs))
    grouped = group_consecutive(uniq)
    verses = [build_verse(node.id, b, c, s, e, kjv) for b, c, s, e in grouped]
    record: dict = {
        "id": node.id,
        "number": node.number,
        "title": node.title,
        "sourcePage": node.start,
    }
    if verses:
        record["verses"] = verses
    if children:
        record["children"] = children
    report_lines.append(
        f"{node.id:32} p.{node.start:3d}-{node.end-1:<3d}  "
        f"{len(verses):3d} entries  {node.number or '·':>5}  {node.title}"
    )
    return record


def walk_find(themes: list[dict], theme_id: str) -> dict | None:
    for theme in themes:
        if theme["id"] == theme_id:
            return theme
        found = walk_find(theme.get("children") or [], theme_id)
        if found:
            return found
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--kjv-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    kjv = load_kjv(args.kjv_dir)
    pages = extract_epub_pages(args.epub)

    report_lines: list[str] = []
    empty: list[str] = []

    parts_out = []
    for part_id, part_title, summary, chapter_ids in PARTS:
        chapters_out = []
        for chapter_id in chapter_ids:
            number, chapter_title = CHAPTERS[chapter_id]
            built = [build_node(node, pages, kjv, report_lines) for node in TREES[chapter_id]]
            themes = []
            for theme in built:
                kept = prune_empty(theme)
                if kept:
                    themes.append(kept)
                else:
                    empty.append(theme["id"])
            if not themes:
                continue
            chapters_out.append(
                {
                    "id": chapter_id,
                    "number": number,
                    "title": chapter_title,
                    "themes": themes,
                }
            )
        if chapters_out:
            parts_out.append(
                {
                    "id": part_id,
                    "title": part_title,
                    "summary": summary,
                    "chapters": chapters_out,
                }
            )

    top_themes = [th for p in parts_out for ch in p["chapters"] for th in ch["themes"]]
    theme_count = sum(count_nodes(th) for th in top_themes)
    verse_count = sum(count_verses(th) for th in top_themes)

    catalog = {
        "meta": {
            "title": "A Collection of the Promises of Scripture",
            "alsoCalled": [
                "Precious Bible Promises",
                "Clarke's Scripture Promises",
                "The Christian's Inheritance",
            ],
            "author": "Samuel Clark",
            "authorYears": "1684–1750",
            "place": "St Albans",
            "edition": "1895 Cardiff edition, edited by Geo. Thomas Clark",
            "source": "https://archive.org/details/collectionofprom00clar",
            "structure": "Original two parts plus appendix (not the modern four-part WStS split)",
            "corpusStatus": "working-extract-from-1895-IA-epub",
            "kjvSource": "Public-domain King James Version (aruljohn/Bible-kjv; 1769/Blayney tradition)",
            "excluded": [
                "No ESV, NASB, NIV, or NET text is bundled or cached.",
                "Tom Stewart's 2009 Historical Perspective essay is not included.",
                "whatsaiththescripture.com was not used as a source.",
            ],
            "themeCount": theme_count,
            "verseEntryCount": verse_count,
            "emptyThemesOmitted": empty,
            "nestedHeads": True,
        },
        "parts": parts_out,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = (
        "\n".join(report_lines)
        + f"\n\nShipped themes: {theme_count}\nShipped verse entries: {verse_count}\n"
        + f"Empty themes omitted: {len(empty)}\n"
    )
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {args.out}")

    # Hard requirements
    free = walk_find(top_themes, "p1-c3-free-access")
    if free is None:
        print("ERROR: Free Access theme missing", file=sys.stderr)
        return 1
    if len(free["verses"]) < 6:
        print("ERROR: Free Access theme is too thin", file=sys.stderr)
        return 1
    if theme_count < 40 or verse_count < 200:
        print("ERROR: corpus subset is too small", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
