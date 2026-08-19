#!/usr/bin/env python3
"""Checks that mirror the Swift search and ESV-link helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "ClarkePromises/ClarkePromises/Resources/clarke-promises.json"

ESV_BOOK = {
    "Psalms": "Psalm",
    "Song of Solomon": "Song+of+Solomon",
}

YOUVERSION = {
    "John": "JHN",
    "Psalms": "PSA",
    "Ephesians": "EPH",
    "1 Peter": "1PE",
    "Hebrews": "HEB",
}


def esv_org_url(book: str, chapter: int, verse: int, end_verse: int | None) -> str:
    name = ESV_BOOK.get(book, book.replace(" ", "+"))
    if end_verse and end_verse != verse:
        ref = f"{name}+{chapter}:{verse}-{end_verse}"
    else:
        ref = f"{name}+{chapter}:{verse}"
    return f"https://www.esv.org/{quote(ref, safe='+:')}/"


def bible_com_url(book: str, chapter: int, verse: int) -> str:
    code = YOUVERSION.get(book, "JHN")
    return f"https://www.bible.com/bible/59/{code}.{chapter}.{verse}"


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node.get("children") or [])


def search(file: dict, query: str) -> list[dict]:
    terms = query.lower().split()
    hits = []
    for part in file["parts"]:
        for chapter in part["chapters"]:
            for theme in walk(chapter["themes"]):
                for verse in theme.get("verses") or []:
                    hay = " ".join(
                        [
                            theme["title"].lower(),
                            verse["displayRef"].lower(),
                            verse["osis"].lower(),
                            verse["book"].lower(),
                            verse["kjv"].lower(),
                        ]
                    )
                    if all(t in hay for t in terms):
                        hits.append({"verse": verse, "theme": theme})
    return hits


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))

    assert esv_org_url("John", 3, 16, None) == "https://www.esv.org/John+3:16/"
    assert esv_org_url("Psalms", 23, 1, 6) == "https://www.esv.org/Psalm+23:1-6/"
    assert esv_org_url("1 Peter", 2, 4, 5) == "https://www.esv.org/1+Peter+2:4-5/"
    assert bible_com_url("John", 3, 16) == "https://www.bible.com/bible/59/JHN.3.16"
    assert bible_com_url("Ephesians", 2, 18) == "https://www.bible.com/bible/59/EPH.2.18"

    access = search(data, "access")
    assert any(h["theme"]["id"] == "p1-c3-free-access" for h in access), access[:3]

    food = search(data, "raiment")
    assert any(h["theme"]["id"] in {"p1-c1-raiment", "p1-c1-food-raiment"} for h in food), food[:3]

    psalm = search(data, "Psalm 23")
    assert psalm, "expected Psalm 23 hits"

    kjv = search(data, "shepherd")
    assert kjv, "expected KJV text hit for shepherd"

    print(
        f"OK: ESV links and nested search "
        f"({len(access)} access, {len(food)} raiment, {len(psalm)} Psalm 23, {len(kjv)} shepherd)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
