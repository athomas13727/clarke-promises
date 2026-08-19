"""1895 Clarke heads as a nested tree (two parts + appendix).

Page numbers are printed pages from the Cardiff 1895 TOC.
EPUB leaf = printed page + 90. Markers slice same-page sibling heads.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    id: str
    title: str
    start: int
    end: int
    number: str | None = None
    curated: list[tuple[str, int, int]] | None = None
    start_marker: str | None = None
    end_marker: str | None = None
    children: list[Node] = field(default_factory=list)


FREE_ACCESS = [
    ("Ephesians", 2, 18),
    ("Ephesians", 3, 12),
    ("1 Peter", 2, 4),
    ("1 Peter", 2, 5),
    ("Hebrews", 10, 19),
    ("Hebrews", 10, 20),
    ("Ephesians", 1, 6),
    ("Ezekiel", 20, 40),
    ("Ezekiel", 20, 41),
]

FAITH = [
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


def n(
    id: str,
    title: str,
    start: int,
    end: int,
    number: str | None = None,
    curated=None,
    start_marker: str | None = None,
    end_marker: str | None = None,
    children: list[Node] | None = None,
) -> Node:
    return Node(
        id=id,
        title=title,
        start=start,
        end=end,
        number=number,
        curated=curated,
        start_marker=start_marker,
        end_marker=end_marker,
        children=children or [],
    )


TREES: dict[str, list[Node]] = {
    "p1-c1": [
        n("p1-c1-general", "General Promises to the Good", 1, 3, "I"),
        n("p1-c1-temporal-general", "Promises of Temporal Blessings in General", 3, 4, "II"),
        n(
            "p1-c1-food-raiment",
            "Particularly of Food and Raiment",
            4,
            6,
            "III",
            start_marker="Particularly of Food",
            end_marker="Long Life",
            children=[
                n(
                    "p1-c1-food",
                    "Food",
                    4,
                    5,
                    start_marker="Of Food",
                ),
                n(
                    "p1-c1-raiment",
                    "Raiment",
                    5,
                    6,
                    start_marker="Promises of Raiment",
                    end_marker="Long Life",
                    curated=[
                        ("Matthew", 6, 25),
                        ("Matthew", 6, 30),
                        ("Matthew", 6, 31),
                        ("Matthew", 6, 32),
                    ],
                ),
            ],
        ),
        n(
            "p1-c1-long-life-health",
            "Of Long Life",
            5,
            7,
            "IV",
            start_marker="Long Life",
            children=[
                n(
                    "p1-c1-long-life",
                    "Long Life",
                    5,
                    6,
                    start_marker="Long Life",
                    end_marker="Health",
                ),
                n("p1-c1-health", "Health", 6, 7, start_marker="Health"),
            ],
        ),
        n("p1-c1-safety", "Safety under the Divine Protection", 7, 11, "V"),
        n("p1-c1-peace", "Peace", 11, 12, "VI"),
        n("p1-c1-direction", "Direction", 12, 13, "VII"),
        n("p1-c1-honour", "Honour", 12, 14, "VIII", start_marker="Honour"),
        n("p1-c1-success", "Success and Prosperity", 14, 15, "IX"),
        n("p1-c1-plenty", "Plenty and Riches", 15, 17, "X"),
        n("p1-c1-children", "Children", 17, 18, "XI"),
        n("p1-c1-blessing-all", "A Blessing upon all a Good Man has", 17, 19, "XII"),
        n("p1-c1-blessing-children", "A Blessing upon his Children", 19, 20, "XIII"),
        n("p1-c1-family", "A Blessing upon his Family", 20, 21, "XIV"),
    ],
    "p1-c2": [
        n(
            "p1-c2-in-general",
            "In General",
            21,
            28,
            "I",
            children=[
                n(
                    "p1-c2-preservation",
                    "Preservation from Trouble",
                    21,
                    23,
                    start_marker="Preservation",
                    end_marker="Job viii",
                    curated=[
                        ("Job", 5, 19),
                        ("Psalms", 31, 23),
                        ("Psalms", 32, 6),
                        ("Psalms", 32, 7),
                        ("Psalms", 91, 10),
                        ("Proverbs", 12, 21),
                    ],
                ),
                n(
                    "p1-c2-deliverance",
                    "Deliverance out of Trouble",
                    22,
                    24,
                    start_marker="Deliverance",
                    end_marker="Support",
                ),
                n("p1-c2-support", "Support under it", 24, 28, start_marker="Support"),
            ],
        ),
        n(
            "p1-c2-sickness-head",
            "Promises relating to Sickness",
            28,
            31,
            "II",
            children=[
                n(
                    "p1-c2-sickness",
                    "Sickness",
                    28,
                    30,
                    start_marker="Sickness",
                    end_marker="Child-bearing",
                ),
                n(
                    "p1-c2-childbearing",
                    "Child-bearing",
                    30,
                    31,
                    start_marker="Child-bearing",
                    end_marker="Old Age",
                ),
                n(
                    "p1-c2-old-age",
                    "Old Age",
                    30,
                    32,
                    start_marker="In Old Age",
                    end_marker="Famine",
                    curated=[
                        ("Psalms", 71, 9),
                        ("Isaiah", 46, 4),
                        ("Proverbs", 16, 31),
                    ],
                ),
            ],
        ),
        n("p1-c2-famine", "Deliverance from Famine and Want", 31, 32, "III"),
        n(
            "p1-c2-war-enemies",
            "From War and Enemies",
            32,
            36,
            "IV",
            children=[
                n(
                    "p1-c2-war",
                    "From War",
                    32,
                    33,
                    start_marker="War",
                    end_marker="Enemies",
                ),
                n("p1-c2-enemies", "From Enemies", 33, 36, start_marker="Enemies"),
            ],
        ),
        n("p1-c2-oppression", "From Oppression and Injustice", 36, 38, "V"),
        n(
            "p1-c2-slander-reproach",
            "From Slanders and Reproach",
            38,
            39,
            "VI",
            children=[
                n(
                    "p1-c2-slander",
                    "Slanders",
                    38,
                    39,
                    start_marker="Slander",
                    end_marker="Reproach",
                ),
                n("p1-c2-reproach", "Reproach", 38, 39, start_marker="Reproach"),
            ],
        ),
        n("p1-c2-witchcraft", "From Witchcraft", 39, 40, "VII"),
        n("p1-c2-stranger", "To the Stranger and Exile", 39, 40, "VIII"),
        n("p1-c2-poor", "To the Poor and Helpless", 40, 41, "IX"),
        n("p1-c2-fatherless", "To the Fatherless and Widow", 41, 43, "X"),
        n("p1-c2-childless", "To the Childless", 43, 44, "XI"),
        n("p1-c2-captive", "To the Prisoner and Captive", 43, 44, "XII"),
        n("p1-c2-death", "Deliverance from Death", 44, 46, "XIII"),
    ],
    "p1-c3": [
        n("p1-c3-spiritual-general", "In General", 46, 47, "I"),
        n(
            "p1-c3-justification",
            "Of Justification",
            47,
            55,
            "II",
            children=[
                n("p1-c3-justification-head", "Justification", 47, 49),
                n(
                    "p1-c3-pardon",
                    "Pardon of Sin",
                    49,
                    52,
                    children=[
                        n("p1-c3-pardon-heinous", "Of the most heinous Sins", 51, 52),
                        n("p1-c3-pardon-all", "Of all Sins", 51, 52),
                        n("p1-c3-pardon-backsliding", "Of Backslidings", 51, 52),
                    ],
                ),
                n("p1-c3-pardon-christ", "Pardon through Christ", 52, 54),
                n("p1-c3-reconciliation", "Reconciliation", 54, 55),
            ],
        ),
        n("p1-c3-adoption", "Adoption", 55, 57, "III"),
        n("p1-c3-union", "Union and Communion with the Church", 57, 59, "IV"),
        n(
            "p1-c3-free-access",
            "Free Access to God, with Acceptance",
            59,
            60,
            "V",
            curated=FREE_ACCESS,
        ),
        n("p1-c3-hearing-prayer", "Of Hearing Prayer", 60, 63, "VI"),
        n("p1-c3-sanctifying", "Of Sanctifying Grace in general", 63, 65, "VII"),
        n(
            "p1-c3-converting",
            "Particularly of Converting Grace",
            65,
            69,
            "VIII",
            children=[
                n("p1-c3-converting-head", "Converting Grace", 65, 67),
                n("p1-c3-repentance-grace", "The Grace of Repentance", 67, 68),
                n("p1-c3-faith-grace", "The Grace of Faith", 68, 69),
                n("p1-c3-fear-grace", "Grace to fear God", 68, 69, start_marker="fear"),
            ],
        ),
        n(
            "p1-c3-knowledge",
            "Of Knowledge",
            69,
            73,
            "IX",
            children=[
                n("p1-c3-knowledge-head", "Knowledge", 69, 71),
                n("p1-c3-wisdom", "Wisdom", 71, 72, start_marker="Wisdom"),
                n("p1-c3-teaching", "Divine Teaching", 71, 72),
                n("p1-c3-guidance", "Divine Guidance", 72, 73),
                n("p1-c3-discourse-ability", "Ability for Good Discourse", 73, 74),
            ],
        ),
        n(
            "p1-c3-means",
            "Of the Means of Grace",
            73,
            77,
            "X",
            children=[
                n("p1-c3-means-head", "The Means of Grace", 73, 75),
                n("p1-c3-means-blessing", "A Blessing upon them", 75, 77),
            ],
        ),
        n(
            "p1-c3-against-sin",
            "Grace against Sin and Temptation",
            77,
            81,
            "XI",
            children=[
                n("p1-c3-mortify", "To mortify Sin", 77, 78),
                n("p1-c3-temptation", "Against Temptation", 78, 79),
                n("p1-c3-enticements", "To preserve from the Enticements of Sinners", 79, 80),
                n("p1-c3-world", "Victory over the World", 79, 80),
                n("p1-c3-devil", "Victory over the Devil", 80, 81),
            ],
        ),
        n("p1-c3-strength", "Strength, Courage, and Resolution", 81, 83, "XII"),
        n(
            "p1-c3-fruitfulness",
            "Fruitfulness and Increase of Grace",
            83,
            85,
            "XIII",
            children=[
                n("p1-c3-fruit-old-age", "Particularly in Old Age", 84, 85),
                n("p1-c3-meekness-grace", "The Grace of Meekness", 85, 86),
            ],
        ),
        n("p1-c3-persevere", "Grace to persevere", 85, 87, "XIV"),
        n("p1-c3-afflictions", "Sanctified Afflictions", 87, 91, "XV"),
        n("p1-c3-believers-children", "Grace to the Children of Believers", 91, 92, "XVI"),
        n(
            "p1-c3-interest-god",
            "An Interest in God",
            92,
            102,
            "XVII",
            children=[
                n("p1-c3-god-our-god", "As our God", 92, 93, start_marker="our God"),
                n("p1-c3-god-portion", "As our Portion", 93, 94, start_marker="Portion"),
                n("p1-c3-god-glory", "Our Glory", 94, 95, start_marker="Glory"),
                n("p1-c3-god-presence", "Of his Presence", 94, 95, start_marker="Presence"),
                n("p1-c3-god-love", "His Love", 95, 96, start_marker="Love"),
                n("p1-c3-god-mercy", "His Mercy", 96, 98, start_marker="Mercy"),
                n("p1-c3-god-help", "His Help", 98, 99, start_marker="Help"),
                n("p1-c3-god-care", "His Care", 99, 100, start_marker="Care"),
                n("p1-c3-god-covenant", "His Covenanting with his people", 100, 102),
                n("p1-c3-god-not-forsake", "That God will not forsake them", 100, 102, start_marker="forsake"),
            ],
        ),
        n(
            "p1-c3-interest-christ",
            "An Interest in Christ",
            102,
            109,
            "XVIII",
            children=[
                n("p1-c3-christ-grace", "All Grace from Him", 103, 104),
                n("p1-c3-christ-redemption", "Redemption by Him", 104, 105),
                n("p1-c3-christ-life", "Life from him", 105, 107),
                n("p1-c3-christ-intercession", "His Intercession", 107, 108),
                n("p1-c3-christ-love", "His Love", 107, 108),
                n("p1-c3-christ-church", "His Care of his Church", 108, 109),
                n("p1-c3-christ-presence", "His Presence with his People", 109, 110),
            ],
        ),
        n(
            "p1-c3-spirit",
            "Promises of the Spirit",
            109,
            114,
            "XIX",
            children=[
                n("p1-c3-spirit-teaching", "His Teaching", 111, 112),
                n("p1-c3-spirit-prayer", "His Help in Prayer", 112, 113),
                n("p1-c3-spirit-adoption", "To witness our Adoption", 112, 113),
                n("p1-c3-spirit-seal", "To seal our Redemption", 112, 113),
                n("p1-c3-spirit-comforter", "To be our Comforter", 113, 114),
                n("p1-c3-spirit-joy", "Joy in the Holy Ghost", 113, 114),
            ],
        ),
        n("p1-c3-angels", "The Ministry of Angels", 114, 115, "XX"),
        n("p1-c3-kings-priests", "That we should be Kings and Priests to God", 114, 115, "XXI"),
        n(
            "p1-c3-conscience",
            "Peace of Conscience",
            115,
            118,
            "XXII",
            children=[
                n("p1-c3-comfort-hope", "Comfort and Hope", 116, 118),
            ],
        ),
        n("p1-c3-joy", "Delight and Joy in God", 118, 121, "XXIII"),
        n("p1-c3-death", "Support in Death", 121, 123, "XXIV"),
    ],
    "p1-c4": [
        n("p1-c4-hell", "Deliverance from Hell", 123, 124, "I"),
        n("p1-c4-after-death", "Happiness immediately after Death", 124, 125, "II"),
        n("p1-c4-resurrection", "A Glorious Resurrection", 125, 130, "III"),
        n(
            "p1-c4-heaven",
            "Everlasting Happiness in Heaven",
            130,
            138,
            "IV",
            children=[
                n("p1-c4-heaven-sorrow", "Freedom from all Sorrow, and great Joy", 134, 135),
                n("p1-c4-heaven-glory", "Glory", 134, 135, start_marker="Glory"),
                n("p1-c4-heaven-kingdom", "A Kingdom", 135, 136),
                n("p1-c4-heaven-inheritance", "An Inheritance", 136, 138),
                n("p1-c4-heaven-god", "The Enjoyment of God, and Eternal Life", 136, 138),
            ],
        ),
    ],
    "p2-c1": [
        n(
            "p2-c1-faith",
            "To Faith, particularly in Christ",
            138,
            141,
            "I",
            curated=FAITH,
            children=[
                n("p2-c1-confessing", "Confessing Christ", 141, 142),
            ],
        ),
        n(
            "p2-c1-repentance",
            "Repentance",
            142,
            148,
            "II",
            children=[
                n("p2-c1-mourn-land", "To them that mourn for the Wickedness of the Land", 145, 146),
                n("p2-c1-repent-affliction", "To Repentance in Affliction", 146, 147),
                n("p2-c1-confess-sin", "To Confession of Sin", 147, 148),
            ],
        ),
        n(
            "p2-c1-obedience",
            "Obedience",
            148,
            155,
            "III",
            children=[
                n("p2-c1-obey-christ", "Obeying Christ", 154, 155),
            ],
        ),
        n("p2-c1-sincerity", "Sincerity and Uprightness", 155, 157, "IV"),
        n(
            "p2-c1-love-god",
            "Love to God",
            157,
            159,
            "V",
            children=[
                n("p2-c1-love-christ", "To Christ", 158, 159),
            ],
        ),
        n("p2-c1-trust", "Trusting and patiently Waiting on God", 159, 162, "VI"),
        n(
            "p2-c1-fear",
            "The Fear of God",
            162,
            164,
            "VII",
            children=[
                n("p2-c1-honour-god", "Honouring God", 164, 165),
            ],
        ),
        n(
            "p2-c1-prayer",
            "Prayer",
            164,
            169,
            "VIII",
            children=[
                n("p2-c1-seeking", "Seeking God", 166, 167),
                n("p2-c1-secret-prayer", "Secret Prayer", 167, 168),
                n("p2-c1-praise", "Praising God", 168, 169),
                n("p2-c1-desires", "Desires of Grace", 168, 169),
            ],
        ),
        n(
            "p2-c1-wisdom",
            "Wisdom and Knowledge",
            169,
            174,
            "IX",
            children=[
                n("p2-c1-love-wisdom", "The Love and Study of Wisdom", 172, 173),
                n("p2-c1-knowledge-god", "The Knowledge of God and Christ", 173, 174),
                n("p2-c1-learn-christ", "Learning from Christ", 174, 175),
            ],
        ),
        n(
            "p2-c1-word",
            "Hearing and Reading the Word of God",
            174,
            177,
            "X",
            children=[
                n("p2-c1-loving-word", "Loving the Word", 177, 178),
                n("p2-c1-trembling", "Trembling at it", 177, 178),
            ],
        ),
        n("p2-c1-meditation", "Meditation", 177, 179, "XI"),
        n(
            "p2-c1-fasting",
            "Fasting",
            179,
            180,
            "XII",
            children=[
                n("p2-c1-fast-secret", "Fasting in Secret", 179, 180),
            ],
        ),
        n("p2-c1-baptism", "Baptism", 180, 181, "XIII"),
        n("p2-c1-supper", "The Lord's Supper", 181, 182, "XIV"),
        n(
            "p2-c1-discourse",
            "Good Discourse",
            182,
            184,
            "XV",
            children=[
                n("p2-c1-tongue", "Government of the Tongue", 184, 185),
            ],
        ),
        n("p2-c1-watch", "Watchfulness", 184, 185, "XVI"),
        n(
            "p2-c1-company",
            "Keeping Good Company",
            185,
            186,
            "XVII",
            children=[
                n("p2-c1-avoid-company", "Avoiding Evil Company", 185, 186),
            ],
        ),
        n("p2-c1-oaths", "Performing Oaths", 185, 186, "XVIII"),
        n("p2-c1-sabbath", "Keeping the Sabbath", 186, 187, "XIX"),
    ],
    "p2-c2": [
        n("p2-c2-parents", "Obedience to Parents", 187, 189, "I"),
        n(
            "p2-c2-education",
            "Good Education",
            189,
            190,
            "II",
            children=[
                n("p2-c2-correction", "The Correcting of Children", 190, 191),
            ],
        ),
        n("p2-c2-wife", "A Good Wife", 190, 191, "III"),
        n("p2-c2-servants", "Faithful Servants", 191, 192, "IV"),
        n("p2-c2-kings", "Good Kings and Magistrates", 192, 193, "V"),
        n("p2-c2-subjects", "Obedient Subjects", 193, 194, "VI"),
        n("p2-c2-ministers", "Faithful Ministers", 193, 197, "VII"),
        n("p2-c2-hear-ministers", "To them that receive and hearken to Ministers", 197, 198, "VIII"),
        n(
            "p2-c2-love",
            "Love and Unity",
            198,
            200,
            "IX",
            children=[
                n("p2-c2-peacemakers", "To the Peace-makers", 198, 199),
                n("p2-c2-love-people", "Love to God's People", 199, 200),
            ],
        ),
        n(
            "p2-c2-charitable",
            "To the Charitable, the Merciful, and Liberal",
            200,
            207,
            "X",
            children=[
                n("p2-c2-alms", "To Alms in secret", 205, 206),
                n("p2-c2-worship", "To supporting God's Worship and Ministers", 205, 207),
                n("p2-c2-merciful", "The Merciful", 207, 208),
            ],
        ),
        n(
            "p2-c2-reproof",
            "Reproving faithfully",
            207,
            208,
            "XI",
            children=[
                n("p2-c2-regarding-reproof", "And regarding Reproof", 208, 209),
            ],
        ),
        n("p2-c2-forgive", "Forgiving Injuries", 208, 209, "XII"),
        n(
            "p2-c2-chastity",
            "Chastity",
            209,
            210,
            "XIII",
            children=[
                n("p2-c2-purity", "Purity", 210, 211),
            ],
        ),
        n(
            "p2-c2-diligence",
            "Diligence",
            210,
            212,
            "XIV",
            children=[
                n("p2-c2-talents", "Improving Talents", 211, 212),
                n("p2-c2-sleep", "Moderation in Sleep", 212, 213),
            ],
        ),
        n("p2-c2-just", "The Just and Honest", 212, 214, "XV"),
        n("p2-c2-truth", "Truth", 214, 215, "XVI"),
        n(
            "p2-c2-candour",
            "Candour in Judging",
            214,
            215,
            "XVII",
            children=[
                n("p2-c2-speaking", "And Speaking", 215, 216),
            ],
        ),
        n("p2-c2-contentment", "Contentment and Mortification", 215, 217, "XVIII"),
    ],
    "p2-c3": [
        n(
            "p2-c3-meek",
            "To the Meek",
            217,
            221,
            "I",
            children=[
                n("p2-c3-humble", "And the Humble", 219, 220),
                n("p2-c3-contrite", "The Contrite and Mourners", 220, 221),
            ],
        ),
        n(
            "p2-c3-suffer",
            "To them that suffer for Righteousness' Sake",
            221,
            223,
            "II",
            children=[
                n("p2-c3-excommunicated", "To them that are unjustly excommunicated", 223, 224),
            ],
        ),
        n("p2-c3-patience", "Patience and Submission", 223, 225, "III"),
        n(
            "p2-c3-perseverance",
            "Perseverance",
            225,
            229,
            "IV",
            children=[
                n("p2-c3-overcometh", "To him that overcometh", 227, 229),
            ],
        ),
    ],
    "apx-c1": [
        n(
            "apx-enlargement",
            "Of the Enlargement of the Church, and Spreading the Gospel",
            229,
            240,
            "I",
        ),
        n("apx-glory", "The Glory of the Church", 240, 243, "II"),
        n("apx-light", "Increase of Light and Means of Grace", 243, 244, "III"),
        n("apx-purity", "Increase of Purity, Holiness, and Righteousness", 244, 247, "IV"),
        n("apx-peace", "Peace, Love, and Unity in the Church", 247, 249, "V"),
        n(
            "apx-enemies",
            "Submission and Destruction of the Enemies of the Church",
            249,
            252,
            "VI",
            children=[
                n("apx-babylon", "Destruction of Antichrist, of Babylon, &c.", 250, 252),
            ],
        ),
        n("apx-kings", "Favour and Submission of Kings to the Kingdom of Christ", 252, 254, "VII"),
        n("apx-security", "Security, Tranquillity, and Prosperity of the Church", 254, 257, "VIII"),
        n("apx-perpetual", "The Perpetual Continuance of the Church", 257, 258, "IX"),
        n("apx-jews", "The Conversion and Restoration of the Jews", 258, 270, "X"),
        n("apx-conclusion", "That God will perform all his Promises", 270, 273, None),
    ],
}
