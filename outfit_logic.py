"""
outfit_logic.py
Pure-Python rule-based matching: no AI, just color-compatibility rules
and occasion filtering, following by a repeat-avoidance pick.
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
