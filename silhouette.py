"""
silhouette.py
Draws a stylized human figure wearing the matched outfit using only Pillow
(ImageDraw shapes) -- no AI, no external image generation.
"""

from PIL import Image, ImageDraw

SKIN_TONES = {
    "Light":  "#F4D9C0",
    "Medium": "#E0AC81",
    "Tan":    "#C68863",
    "Deep":   "#8D5524",
    "Dark":   "#4A2C1B",
}

COLOR_HEX = {
    "white":  "#F5F5F5",
    "black":  "#2B2B2B",
    "grey":   "#9CA3AF",
    "blue":   "#3B82F6",
    "navy":   "#1E3A5F",
    "red":    "#EF4444",
    "green":  "#22C55E",
    "yellow": "#EAB308",
    "brown":  "#92400E",
    "beige":  "#D8C3A5",
    "pink":   "#EC4899",
    "purple": "#8B5CF6",
    "orange": "#F97316",
}


def _hex(color_name, fallback="#9CA3AF"):
    return COLOR_HEX.get((color_name or "").lower(), fallback)


def draw_silhouette(top_color, bottom_color, shoes_color, skin_tone="Medium", size=(320, 640)):
    """Returns a PIL.Image of a human figure wearing the given outfit colors."""
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    skin = SKIN_TONES.get(skin_tone, SKIN_TONES["Medium"])
    top_hex = _hex(top_color, "#3B82F6")
    bottom_hex = _hex(bottom_color, "#9CA3AF")
    shoes_hex = _hex(shoes_color, "#EF4444")

    cx = W // 2
    outline = "#00000022"

    # --- Head + neck ---
    draw.ellipse([cx - 46, 18, cx + 46, 112], fill=skin, outline=outline, width=2)
    draw.rectangle([cx - 16, 104, cx + 16, 140], fill=skin)

    # --- Simple hair cap (keeps the figure gender-neutral & friendly) ---
    draw.pieslice([cx - 46, 8, cx + 46, 90], start=180, end=360, fill="#3b2a20")

    # --- Torso (shirt) ---
    draw.polygon(
        [(cx - 88, 168), (cx + 88, 168), (cx + 100, 310), (cx - 100, 310)],
        fill=top_hex, outline=outline,
    )

    # --- Arms (skin) ---
    draw.polygon(
        [(cx - 88, 168), (cx - 136, 300), (cx - 108, 312), (cx - 72, 188)],
        fill=skin, outline=outline,
    )
    draw.polygon(
        [(cx + 88, 168), (cx + 136, 300), (cx + 108, 312), (cx + 72, 188)],
        fill=skin, outline=outline,
    )

    # --- Hips / upper legs (pants) ---
    draw.polygon(
        [(cx - 94, 305), (cx + 94, 305), (cx + 84, 480), (cx - 84, 480)],
        fill=bottom_hex, outline=outline,
    )
    # leg gap
    draw.line([(cx, 380), (cx, 480)], fill=(0, 0, 0, 40), width=3)
    draw.rectangle([cx - 84, 475, cx - 14, 575], fill=bottom_hex, outline=outline)
    draw.rectangle([cx + 14, 475, cx + 84, 575], fill=bottom_hex, outline=outline)

    # --- Shoes ---
    draw.rounded_rectangle([cx - 90, 568, cx - 8, 610], radius=12, fill=shoes_hex, outline=outline)
    draw.rounded_rectangle([cx + 8, 568, cx + 90, 610], radius=12, fill=shoes_hex, outline=outline)

    return img
