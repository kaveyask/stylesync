"""
outfit_logic.py
Pure-Python rule-based matching: no AI, just color-compatibility rules,
occasion filtering, a repeat-avoidance pick, and a deterministic
"Match Score" so outfits can be ranked/displayed without any model calls.
"""

import random
from itertools import product

# Which colors are considered compatible with which (kept intentionally simple).
COLOR_MATCHES = {
    "white":  ["black", "blue", "grey", "navy", "brown", "red", "green", "pink", "purple", "beige", "white"],
    "black":  ["white", "grey", "red", "blue", "pink", "yellow", "beige", "black"],
    "grey":   ["white", "black", "blue", "navy", "pink", "purple", "grey"],
    "blue":   ["white", "grey", "black", "beige", "navy", "blue"],
    "navy":   ["white", "grey", "beige", "blue", "navy"],
    "red":    ["white", "black", "grey", "beige", "red"],
    "green":  ["white", "beige", "brown", "grey", "green"],
    "yellow": ["black", "white", "grey", "navy", "yellow"],
    "brown":  ["white", "beige", "green", "blue", "brown"],
    "beige":  ["white", "black", "blue", "navy", "green", "brown", "beige"],
    "pink":   ["white", "grey", "black", "navy", "pink"],
    "purple": ["white", "grey", "black", "purple"],
    "orange": ["white", "black", "navy", "beige", "orange"],
}

# Especially strong, "editor's pick" color pairings -> these score higher
# than merely-compatible pairs when we compute the Match Score.
PREMIUM_PAIRS = {
    frozenset(("black", "white")),
    frozenset(("navy", "white")),
    frozenset(("navy", "beige")),
    frozenset(("white", "beige")),
    frozenset(("black", "beige")),
    frozenset(("grey", "black")),
    frozenset(("brown", "beige")),
    frozenset(("white", "blue")),
}


def colors_compatible(c1, c2):
    c1, c2 = c1.lower(), c2.lower()
    return c2 in COLOR_MATCHES.get(c1, []) or c1 in COLOR_MATCHES.get(c2, [])


def generate_valid_outfits(tops, bottoms, shoes):
    """tops/bottoms/shoes are lists of dict rows from the clothes table
    (already filtered to the same occasion by the caller)."""
    valid = []
    for t, b, s in product(tops, bottoms, shoes):
        if not colors_compatible(t["color"], b["color"]):
            continue
        if not colors_compatible(t["color"], s["color"]):
            continue
        if not colors_compatible(b["color"], s["color"]):
            continue
        valid.append((t, b, s))
    return valid


def pick_outfit(valid_outfits, recent_ids):
    """Prefer a combo not worn recently; fall back to any valid combo."""
    fresh = [
        o for o in valid_outfits
        if (o[0]["id"], o[1]["id"], o[2]["id"]) not in recent_ids
    ]
    pool = fresh if fresh else valid_outfits
    return random.choice(pool) if pool else None


def _pair_score(c1, c2):
    c1, c2 = c1.lower(), c2.lower()
    if frozenset((c1, c2)) in PREMIUM_PAIRS:
        return 100
    if colors_compatible(c1, c2):
        return 75
    return 40  # shouldn't occur for a valid outfit, kept as a safe floor


def calculate_match_score(top, bottom, shoe, recent_ids=None):
    """Deterministic 0-100 compatibility score for a (top, bottom, shoe)
    combo. No AI/model calls involved - just a weighted rule set:

    - 80% of the score comes from how strong the three color pairings are
    - up to +10 bonus for not being a repeat of a recently-worn combo
    """
    pair_scores = [
        _pair_score(top["color"], bottom["color"]),
        _pair_score(top["color"], shoe["color"]),
        _pair_score(bottom["color"], shoe["color"]),
    ]
    base = sum(pair_scores) / len(pair_scores)

    bonus = 0
    if recent_ids is not None:
        combo = (top["id"], bottom["id"], shoe["id"])
        bonus = 10 if combo not in recent_ids else -5

    return max(0, min(100, round(base + bonus)))
