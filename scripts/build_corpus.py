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

# 1895 printed-page ranges from the edition TOC (inclusive start, exclusive end).
# Page mapping used by extract_epub_pages(): printed N => EPUB page N+90.
THEMES = [
    # Part I ch. 1
    ("part-1", "p1-c1", "p1-c1-general", "General Promises to the Good", 1, 3, None),
    ("part-1", "p1-c1", "p1-c1-temporal-general", "Temporal Blessings in General", 3, 4, None),
    ("part-1", "p1-c1", "p1-c1-food-raiment", "Food and Raiment", 4, 5, None),
    ("part-1", "p1-c1", "p1-c1-long-life-health", "Long Life and Health", 5, 7, None),
    ("part-1", "p1-c1", "p1-c1-safety", "Safety under the Divine Protection", 7, 11, None),
    ("part-1", "p1-c1", "p1-c1-peace", "Peace", 11, 12, None),
    ("part-1", "p1-c1", "p1-c1-direction-honour", "Direction and Honour", 12, 14, None),
    ("part-1", "p1-c1", "p1-c1-success", "Success and Prosperity", 14, 15, None),
    ("part-1", "p1-c1", "p1-c1-plenty", "Plenty and Riches", 15, 17, None),
    ("part-1", "p1-c1", "p1-c1-children", "Children, and a Blessing upon All He Has", 17, 19, None),
    ("part-1", "p1-c1", "p1-c1-blessing-children", "A Blessing upon His Children", 19, 20, None),
    ("part-1", "p1-c1", "p1-c1-family", "A Blessing upon His Family", 20, 21, None),
    # Part I ch. 2
    ("part-1", "p1-c2", "p1-c2-preservation", "Preservation from Trouble", 21, 22, None),
    ("part-1", "p1-c2", "p1-c2-deliverance", "Deliverance out of Trouble", 22, 24, None),
    ("part-1", "p1-c2", "p1-c2-support", "Support under Trouble", 24, 28, None),
    ("part-1", "p1-c2", "p1-c2-sickness", "Sickness, Child-bearing, and Old Age", 28, 31, None),
    ("part-1", "p1-c2", "p1-c2-famine", "Deliverance from Famine and Want", 31, 32, None),
    ("part-1", "p1-c2", "p1-c2-war", "Deliverance from War and Enemies", 32, 36, None),
    ("part-1", "p1-c2", "p1-c2-oppression", "Oppression and Injustice", 36, 38, None),
    ("part-1", "p1-c2", "p1-c2-slander", "Slanders and Reproach", 38, 39, None),
    ("part-1", "p1-c2", "p1-c2-stranger", "The Stranger, Exile, and Witchcraft", 39, 40, None),
    ("part-1", "p1-c2", "p1-c2-poor", "The Poor and Helpless", 40, 41, None),
    ("part-1", "p1-c2", "p1-c2-fatherless", "The Fatherless and Widow", 41, 43, None),
    ("part-1", "p1-c2", "p1-c2-childless-captive", "The Childless, Prisoner, and Captive", 43, 44, None),
    ("part-1", "p1-c2", "p1-c2-death", "Deliverance from Death", 44, 46, None),
    # Part I ch. 3
    ("part-1", "p1-c3", "p1-c3-spiritual-general", "Spiritual Blessings in General", 46, 47, None),
    ("part-1", "p1-c3", "p1-c3-justification", "Justification", 47, 49, None),
    ("part-1", "p1-c3", "p1-c3-pardon", "Pardon of Sin", 49, 52, None),
    ("part-1", "p1-c3", "p1-c3-pardon-christ", "Pardon through Christ, and Reconciliation", 52, 55, None),
    ("part-1", "p1-c3", "p1-c3-adoption", "Adoption", 55, 57, None),
    ("part-1", "p1-c3", "p1-c3-union", "Union and Communion with the Church", 57, 59, None),
    (
        "part-1",
        "p1-c3",
        "p1-c3-free-access",
        "Free Access to God, with Acceptance",
        59,
        60,
        [
            ("Ephesians", 2, 18),
            ("Ephesians", 3, 12),
            ("1 Peter", 2, 4),
            ("1 Peter", 2, 5),
            ("Hebrews", 10, 19),
            ("Hebrews", 10, 20),
            ("Ephesians", 1, 6),
            ("Ezekiel", 20, 40),
            ("Ezekiel", 20, 41),
        ],
    ),
    ("part-1", "p1-c3", "p1-c3-hearing-prayer", "Hearing Prayer", 60, 63, None),
    ("part-1", "p1-c3", "p1-c3-sanctifying", "Sanctifying Grace", 63, 65, None),
    ("part-1", "p1-c3", "p1-c3-converting", "Converting Grace, Repentance, and Faith", 65, 69, None),
    ("part-1", "p1-c3", "p1-c3-knowledge", "Knowledge, Wisdom, and Divine Guidance", 69, 73, None),
    ("part-1", "p1-c3", "p1-c3-means", "The Means of Grace", 73, 77, None),
    ("part-1", "p1-c3", "p1-c3-against-sin", "Grace against Sin and Temptation", 77, 81, None),
    ("part-1", "p1-c3", "p1-c3-strength", "Strength, Courage, and Resolution", 81, 83, None),
    ("part-1", "p1-c3", "p1-c3-fruitfulness", "Fruitfulness and Increase of Grace", 83, 85, None),
    ("part-1", "p1-c3", "p1-c3-persevere", "Grace to Persevere", 85, 87, None),
    ("part-1", "p1-c3", "p1-c3-afflictions", "Sanctified Afflictions", 87, 91, None),
    ("part-1", "p1-c3", "p1-c3-believers-children", "Grace to the Children of Believers", 91, 92, None),
    ("part-1", "p1-c3", "p1-c3-interest-god", "An Interest in God", 92, 102, None),
    ("part-1", "p1-c3", "p1-c3-interest-christ", "An Interest in Christ", 102, 109, None),
    ("part-1", "p1-c3", "p1-c3-spirit", "Promises of the Spirit", 109, 114, None),
    ("part-1", "p1-c3", "p1-c3-angels-priests", "Ministry of Angels; Kings and Priests", 114, 115, None),
    ("part-1", "p1-c3", "p1-c3-conscience", "Peace of Conscience, Comfort, and Hope", 115, 118, None),
    ("part-1", "p1-c3", "p1-c3-joy", "Delight and Joy in God", 118, 121, None),
    ("part-1", "p1-c3", "p1-c3-death", "Support in Death", 121, 123, None),
    # Part I ch. 4 — 1895 djvu.txt truncates here; EPUB continues
    ("part-1", "p1-c4", "p1-c4-hell", "Deliverance from Hell", 123, 124, None),
    ("part-1", "p1-c4", "p1-c4-after-death", "Happiness immediately after Death", 124, 125, None),
    ("part-1", "p1-c4", "p1-c4-resurrection", "A Glorious Resurrection", 125, 130, None),
    ("part-1", "p1-c4", "p1-c4-heaven", "Everlasting Happiness in Heaven", 130, 138, None),
    # Part II ch. 1
    (
        "part-2",
        "p2-c1",
        "p2-c1-faith",
        "Faith, particularly in Christ",
        138,
        141,
        [
            ("Isaiah", 28, 16),
            ("1 Peter", 2, 6),
            ("Isaiah", 45, 22),
            ("Mark", 9, 23),
            ("John", 1, 12),
            ("John", 3, 16),
            ("John", 3, 36),
            ("Romans", 4, 5),
            ("Romans", 10, 9),
            ("Romans", 10, 11),
            ("Ephesians", 2, 8),
        ],
    ),
    ("part-2", "p2-c1", "p2-c1-confessing", "Confessing Christ", 141, 142, None),
    ("part-2", "p2-c1", "p2-c1-repentance", "Repentance", 142, 147, None),
    ("part-2", "p2-c1", "p2-c1-obedience", "Obedience and Obeying Christ", 148, 155, None),
    ("part-2", "p2-c1", "p2-c1-sincerity", "Sincerity and Uprightness", 155, 157, None),
    ("part-2", "p2-c1", "p2-c1-love-god", "Love to God and to Christ", 157, 159, None),
    ("part-2", "p2-c1", "p2-c1-trust", "Trusting and Patiently Waiting on God", 159, 162, None),
    ("part-2", "p2-c1", "p2-c1-fear", "The Fear of God, and Honouring God", 162, 164, None),
    ("part-2", "p2-c1", "p2-c1-prayer", "Prayer, Seeking God, and Praise", 164, 169, None),
    ("part-2", "p2-c1", "p2-c1-wisdom", "Wisdom and Knowledge", 169, 174, None),
    ("part-2", "p2-c1", "p2-c1-word", "Hearing, Reading, and Loving the Word", 174, 177, None),
    ("part-2", "p2-c1", "p2-c1-meditation", "Meditation", 177, 179, None),
    ("part-2", "p2-c1", "p2-c1-fasting", "Fasting", 179, 180, None),
    ("part-2", "p2-c1", "p2-c1-baptism", "Baptism", 180, 181, None),
    ("part-2", "p2-c1", "p2-c1-supper", "The Lord's Supper", 181, 182, None),
    ("part-2", "p2-c1", "p2-c1-discourse", "Good Discourse and Government of the Tongue", 182, 184, None),
    ("part-2", "p2-c1", "p2-c1-watch", "Watchfulness", 184, 185, None),
    ("part-2", "p2-c1", "p2-c1-company", "Keeping Good Company", 185, 186, None),
    ("part-2", "p2-c1", "p2-c1-sabbath", "Performing Oaths and Keeping the Sabbath", 185, 187, None),
    # Part II ch. 2
    ("part-2", "p2-c2", "p2-c2-parents", "Obedience to Parents", 187, 189, None),
    ("part-2", "p2-c2", "p2-c2-education", "Good Education and Correcting Children", 189, 190, None),
    ("part-2", "p2-c2", "p2-c2-wife", "A Good Wife", 190, 191, None),
    ("part-2", "p2-c2", "p2-c2-servants", "Faithful Servants", 191, 192, None),
    ("part-2", "p2-c2", "p2-c2-kings", "Good Kings, Magistrates, and Subjects", 192, 193, None),
    ("part-2", "p2-c2", "p2-c2-ministers", "Faithful Ministers", 193, 197, None),
    ("part-2", "p2-c2", "p2-c2-hear-ministers", "Receiving and Hearkening to Ministers", 197, 198, None),
    ("part-2", "p2-c2", "p2-c2-love", "Love, Unity, and the Peace-makers", 198, 200, None),
    ("part-2", "p2-c2", "p2-c2-charitable", "The Charitable, Merciful, and Liberal", 200, 207, None),
    ("part-2", "p2-c2", "p2-c2-reproof", "Giving and Receiving Reproof", 207, 208, None),
    ("part-2", "p2-c2", "p2-c2-forgive", "Forgiving Injuries", 208, 209, None),
    ("part-2", "p2-c2", "p2-c2-chastity", "Chastity and Purity", 209, 210, None),
    ("part-2", "p2-c2", "p2-c2-diligence", "Diligence and Improving Talents", 210, 212, None),
    ("part-2", "p2-c2", "p2-c2-just", "The Just and Honest", 212, 214, None),
    ("part-2", "p2-c2", "p2-c2-truth-candour", "Truth and Candour", 214, 215, None),
    ("part-2", "p2-c2", "p2-c2-contentment", "Contentment and Mortification", 215, 217, None),
    # Part II ch. 3
    ("part-2", "p2-c3", "p2-c3-meek", "The Meek, Humble, and Contrite", 217, 221, None),
    ("part-2", "p2-c3", "p2-c3-suffer", "Them that Suffer for Righteousness' Sake", 221, 223, None),
    ("part-2", "p2-c3", "p2-c3-patience", "Patience and Submission", 223, 225, None),
    ("part-2", "p2-c3", "p2-c3-perseverance", "Perseverance, and Him that Overcometh", 225, 229, None),
    # Appendix
    ("appendix", "apx-c1", "apx-enlargement", "Enlargement of the Church and Spread of the Gospel", 229, 240, None),
    ("appendix", "apx-c1", "apx-glory", "The Glory of the Church", 240, 243, None),
    ("appendix", "apx-c1", "apx-light", "Increase of Light and Means of Grace", 243, 244, None),
    ("appendix", "apx-c1", "apx-purity", "Increase of Purity, Holiness, and Righteousness", 244, 247, None),
    ("appendix", "apx-c1", "apx-peace", "Peace, Love, and Unity in the Church", 247, 249, None),
    ("appendix", "apx-c1", "apx-enemies", "Enemies of the Church, and Destruction of Babylon", 249, 252, None),
    ("appendix", "apx-c1", "apx-kings", "Kings Submit to the Kingdom of Christ", 252, 254, None),
    ("appendix", "apx-c1", "apx-security", "Security, Tranquillity, and Prosperity of the Church", 254, 257, None),
    ("appendix", "apx-c1", "apx-perpetual", "Perpetual Continuance of the Church", 257, 258, None),
    ("appendix", "apx-c1", "apx-jews", "Conversion and Restoration of the Jews", 258, 270, None),
    ("appendix", "apx-c1", "apx-conclusion", "That God Will Perform All His Promises", 270, 273, None),
]

CHAPTERS = {
    "p1-c1": (1, "Promises of Temporal Blessings"),
    "p1-c2": (2, "Promises relating to the Troubles of Life"),
    "p1-c3": (3, "Promises of Spiritual Blessings in this Life"),
    "p1-c4": (4, "Promises of Blessings in the Other World"),
    "p2-c1": (1, "Promises to Duties of the First Table"),
    "p2-c2": (2, "Promises to Duties of the Second Table"),
    "p2-c3": (3, "Promises to Duties belonging to Both Tables"),
    "apx-c1": (1, "Promises relating to the State of the Church"),
}

PARTS = [
    (
        "part-1",
        "The Blessings Promised",
        "Part I. The blessings promised to the good.",
        ["p1-c1", "p1-c2", "p1-c3", "p1-c4"],
    ),
    (
        "part-2",
        "Duties to which Promises Are Made",
        "Part II. Promises to several graces and duties.",
        ["p2-c1", "p2-c2", "p2-c3"],
    ),
    (
        "appendix",
        "Appendix: The Future State of the Church",
        "An appendix of promises relating to the state of the Church, with the conclusion.",
        ["apx-c1"],
    ),
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

    # Ixxxiv / Iviii / Ixv often mean lxxxiv / lviii / lxv
    roman = collapsed.lower().replace("j", "i")
    add(roman_to_int(roman))
    if roman.startswith("i") and len(roman) >= 3 and roman[1] in "xvl":
        add(roman_to_int("l" + roman[1:]))
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

    if re.fullmatch(r"\d{1,3}", collapsed):
        add(int(collapsed))
        return candidates
    add(roman_to_int(collapsed.lower()))
    if collapsed.lower().startswith("i") and len(collapsed) >= 3:
        add(roman_to_int("l" + collapsed.lower()[1:]))
    # "1 2" => 12
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
    for printed in range(start, end):
        epub = printed_to_epub(printed)
        if epub in pages:
            chunks.append(pages[epub])
    return "\n".join(chunks)


def normalize_for_refs(text: str) -> str:
    text = text.replace("[ohn", "John").replace("[ohn", "John")
    text = text.replace("fohn", "John").replace("fob", "Job").replace("iob", "Job")
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
    (?P<name>[A-Za-z\[\]]{2,12})\.
    \s+
    (?P<chap>[ivxlcdmIVXLCDM0-9][ivxlcdmIVXLCDM0-9\s]{0,10})
    \.
    \s*
    (?P<verse>[ivxlcdmIVXLCDM0-9][ivxlcdmIVXLCDM0-9\s]{0,6})
    """,
    re.VERBOSE,
)

VER_RE = re.compile(
    r"""
    \bVer(?:se)?\.?\s*
    (?P<verse>[ivxlcdmIVXLCDM0-9]{1,6})
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
        # Psalm OCR: "Ps. 1. 15" is often Ps. l. 15 (50)
        if book == "Psalms":
            extras = []
            for ch in chapters:
                if ch == 1:
                    extras.append(50)
                if ch == 114:
                    extras.append(145)
            for ch in extras:
                for vs in verses:
                    if (book, ch, vs) in kjv:
                        accept(book, ch, vs)
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epub", required=True, type=Path)
    parser.add_argument("--kjv-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    kjv = load_kjv(args.kjv_dir)
    pages = extract_epub_pages(args.epub)

    theme_records = []
    report_lines = []
    total_verses = 0
    empty = []

    for part_id, chapter_id, theme_id, title, start, end, curated in THEMES:
        text = pages_text(pages, start, end)
        refs = parse_refs(text, kjv)
        if curated:
            for item in curated:
                if item not in refs:
                    refs.append(item)
        # stable unique
        uniq = list(OrderedDict.fromkeys(refs))
        grouped = group_consecutive(uniq)
        verses = [build_verse(theme_id, b, c, s, e, kjv) for b, c, s, e in grouped]
        theme_records.append(
            {
                "partId": part_id,
                "chapterId": chapter_id,
                "id": theme_id,
                "title": title,
                "sourcePage": start,
                "verses": verses,
            }
        )
        total_verses += len(verses)
        status = f"{len(verses):3d} entries / {len(uniq):3d} verses"
        report_lines.append(f"{theme_id:28} p.{start:3d}-{end-1:<3d}  {status}  {title}")
        if not verses:
            empty.append(theme_id)

    parts_out = []
    for part_id, part_title, summary, chapter_ids in PARTS:
        chapters_out = []
        for chapter_id in chapter_ids:
            number, chapter_title = CHAPTERS[chapter_id]
            themes = [t for t in theme_records if t["chapterId"] == chapter_id and t["verses"]]
            if not themes:
                continue
            chapters_out.append(
                {
                    "id": chapter_id,
                    "number": number,
                    "title": chapter_title,
                    "themes": [
                        {
                            "id": t["id"],
                            "title": t["title"],
                            "sourcePage": t["sourcePage"],
                            "verses": t["verses"],
                        }
                        for t in themes
                    ],
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

    theme_count = sum(len(ch["themes"]) for p in parts_out for ch in p["chapters"])
    verse_count = sum(
        len(th["verses"]) for p in parts_out for ch in p["chapters"] for th in ch["themes"]
    )

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
    free = next(
        th
        for p in parts_out
        for ch in p["chapters"]
        for th in ch["themes"]
        if th["id"] == "p1-c3-free-access"
    )
    if len(free["verses"]) < 6:
        print("ERROR: Free Access theme is too thin", file=sys.stderr)
        return 1
    if theme_count < 40 or verse_count < 200:
        print("ERROR: corpus subset is too small", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
