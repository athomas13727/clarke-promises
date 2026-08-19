#!/usr/bin/env python3
"""Validate the bundled catalog: schema, required theme, KJV-only text."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "ClarkePromises/ClarkePromises/Resources/clarke-promises.json"

# Distinctive modern-translation samples that must never appear as verse text.
FORBIDDEN_VERSE_SNIPPETS = [
    "that whoever believes in him should not perish but have eternal life",  # ESV John 3:16
    "For God so loved the world that he gave his one and only Son",  # NIV John 3:16
    "that whoever believes in Him shall not perish, but have eternal life",  # NASB
    "everyone who believes in him will not perish but will have eternal life",  # NET
]

KJV_JOHN_316 = "only begotten Son"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    meta = data["meta"]
    parts = data["parts"]

    if len(parts) != 3:
        fail(f"expected 3 top-level parts (2 + appendix), got {len(parts)}")
    if parts[0]["id"] != "part-1" or parts[1]["id"] != "part-2" or parts[2]["id"] != "appendix":
        fail("parts must be part-1, part-2, appendix")

    themes = [th for p in parts for ch in p["chapters"] for th in ch["themes"]]
    verses = [v for th in themes for v in th["verses"]]
    if len(themes) < 40:
        fail(f"too few themes: {len(themes)}")
    if len(verses) < 200:
        fail(f"too few verse entries: {len(verses)}")

    free = next((th for th in themes if th["id"] == "p1-c3-free-access"), None)
    if not free:
        fail("missing required theme p1-c3-free-access")
    if free["title"] != "Free Access to God, with Acceptance":
        fail("Free Access title does not match Clark")
    osises = {v["osis"] for v in free["verses"]}
    for needed in ("Eph.2.18", "Eph.3.12", "Heb.10.19-20"):
        if needed not in osises:
            fail(f"Free Access missing {needed}")

    for verse in verses:
        for key in ("id", "osis", "displayRef", "book", "chapter", "verse", "kjv"):
            if key not in verse or verse[key] in ("", None):
                fail(f"verse missing {key}: {verse.get('id')}")
        if not isinstance(verse["chapter"], int) or not isinstance(verse["verse"], int):
            fail(f"non-int chapter/verse in {verse['id']}")
        text = verse["kjv"]
        if len(text) < 8:
            fail(f"suspiciously short KJV in {verse['id']}")
        low = text.lower()
        for snippet in FORBIDDEN_VERSE_SNIPPETS:
            if snippet.lower() in low:
                fail(f"modern-translation wording in {verse['id']}")

    john = [v for v in verses if v["osis"].startswith("John.3.16")]
    if john and KJV_JOHN_316 not in john[0]["kjv"]:
        fail("John 3:16 is not the public-domain KJV wording")

    # Repo-wide: no dedicated modern-translation dumps
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in path.parts for part in (".git",)):
            continue
        name = path.name.lower()
        if re.search(r"\b(esv|nasb|niv|net)\b", name) and path.suffix in {".json", ".txt", ".xml"}:
            fail(f"forbidden translation data file: {path}")

    print(
        f"OK: {len(parts)} parts, {len(themes)} themes, {len(verses)} entries, "
        f"Free Access={len(free['verses'])} verses"
    )
    print(f"meta.kjvSource={meta['kjvSource']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
