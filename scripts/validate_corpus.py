#!/usr/bin/env python3
"""Validate the bundled catalog: nested 1895 heads, required theme, KJV-only text."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "ClarkePromises/ClarkePromises/Resources/clarke-promises.json"

FORBIDDEN_VERSE_SNIPPETS = [
    "that whoever believes in him should not perish but have eternal life",
    "For God so loved the world that he gave his one and only Son",
    "that whoever believes in Him shall not perish, but have eternal life",
    "everyone who believes in him will not perish but will have eternal life",
]

KJV_JOHN_316 = "only begotten Son"

REQUIRED_CHILDREN = {
    "p1-c1-food-raiment": {"p1-c1-food", "p1-c1-raiment"},
    "p1-c1-long-life-health": {"p1-c1-long-life", "p1-c1-health"},
    "p1-c2-in-general": {"p1-c2-preservation", "p1-c2-deliverance", "p1-c2-support"},
    "p1-c2-sickness-head": {"p1-c2-sickness", "p1-c2-old-age"},
    "p1-c2-war-enemies": {"p1-c2-war", "p1-c2-enemies"},
    "p1-c2-slander-reproach": {"p1-c2-slander", "p1-c2-reproach"},
    "p1-c3-justification": {"p1-c3-pardon"},
    "p1-c3-converting": {"p1-c3-converting-head", "p1-c3-faith-grace"},
    "p1-c3-knowledge": {"p1-c3-wisdom"},
    "p1-c3-interest-god": {"p1-c3-god-our-god", "p1-c3-god-mercy"},
    "p1-c3-interest-christ": {"p1-c3-christ-redemption"},
    "p1-c3-spirit": {"p1-c3-spirit-teaching", "p1-c3-spirit-comforter"},
    "p1-c4-heaven": {"p1-c4-heaven-sorrow", "p1-c4-heaven-kingdom"},
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def walk(nodes: list[dict]) -> list[dict]:
    out = []
    for node in nodes:
        out.append(node)
        out.extend(walk(node.get("children") or []))
    return out


def find(nodes: list[dict], theme_id: str) -> dict | None:
    for node in nodes:
        if node["id"] == theme_id:
            return node
        found = find(node.get("children") or [], theme_id)
        if found:
            return found
    return None


def verses_of(node: dict) -> list[dict]:
    found = list(node.get("verses") or [])
    for child in node.get("children") or []:
        found.extend(verses_of(child))
    return found


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    meta = data["meta"]
    parts = data["parts"]

    if len(parts) != 3:
        fail(f"expected 3 top-level parts (2 + appendix), got {len(parts)}")
    if [p["id"] for p in parts] != ["part-1", "part-2", "appendix"]:
        fail("parts must be part-1, part-2, appendix")

    top = [th for p in parts for ch in p["chapters"] for th in ch["themes"]]
    themes = walk(top)
    verses = []
    for theme in themes:
        verses.extend(theme.get("verses") or [])

    if len(themes) < 80:
        fail(f"too few nested heads: {len(themes)}")
    if len(verses) < 200:
        fail(f"too few verse entries: {len(verses)}")

    flattened_titles = {
        "Food and Raiment",
        "Food and raiment",
        "Long Life and Health",
        "Long life and health",
        "Sickness, Child-bearing, and Old Age",
        "Deliverance from War and Enemies",
        "Slanders and Reproach",
    }
    for theme in themes:
        if theme["title"] in flattened_titles and not theme.get("children"):
            fail(f"flattened head still present: {theme['title']}")
        number = theme.get("number")
        if number not in (None, "") and not str(number).isdigit():
            fail(f"{theme['id']} number must be Arabic digits, got {number!r}")

    required_titles = {
        "p1-c1-general": "General promises to believers",
        "p1-c1-food-raiment": "Food and raiment",
        "p1-c1-long-life-health": "Long life and health",
        "p1-c1-peace": "Promises of peace",
    }
    for theme_id, title in required_titles.items():
        node = find(top, theme_id)
        if node is None:
            fail(f"missing required theme {theme_id}")
        if node["title"] != title:
            fail(f"{theme_id} title must be {title!r}, got {node['title']!r}")

    for parent_id, child_ids in REQUIRED_CHILDREN.items():
        parent = find(top, parent_id)
        if parent is None:
            fail(f"missing parent {parent_id}")
        have = {child["id"] for child in parent.get("children") or []}
        missing = child_ids - have
        if missing:
            fail(f"{parent_id} missing children {sorted(missing)}")

    free = find(top, "p1-c3-free-access")
    if not free:
        fail("missing required theme p1-c3-free-access")
    if free["title"] != "Free access to God, with acceptance":
        fail("Free Access title does not match Clark")
    osises = {v["osis"] for v in free.get("verses") or []}
    for needed in ("Eph.2.18", "Eph.3.12", "Heb.10.19-20"):
        if needed not in osises:
            fail(f"Free Access missing {needed}")

    for verse in verses:
        for key in ("id", "osis", "displayRef", "book", "chapter", "verse", "kjv"):
            if key not in verse or verse[key] in ("", None):
                fail(f"verse missing {key}: {verse.get('id')}")
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

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        name = path.name.lower()
        if re.search(r"\b(esv|nasb|niv|net)\b", name) and path.suffix in {".json", ".txt", ".xml"}:
            fail(f"forbidden translation data file: {path}")

    print(
        f"OK: {len(parts)} parts, {len(themes)} nested heads, {len(verses)} entries, "
        f"Free Access={len(free.get('verses') or [])} verses"
    )
    print(f"meta.kjvSource={meta['kjvSource']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
