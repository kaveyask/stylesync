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


def draw_silhouette(
    top_color,
    bottom_color,
    shoes_color,
    skin_tone="Medium",
    gender="Female",
    size=(320, 640),
):
    """Return a stylized fashion mannequin for the selected gender."""
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    skin = SKIN_TONES.get(skin_tone, SKIN_TONES["Medium"])
    top_hex = _hex(top_color, "#3B82F6")
    bottom_hex = _hex(bottom_color, "#9CA3AF")
    shoes_hex = _hex(shoes_color, "#EF4444")

    cx = W // 2
    outline = "#00000022"
    is_female = str(gender).strip().lower() == "female"

    # --- Head + neck ---
    draw.ellipse([cx - 46, 18, cx + 46, 112], fill=skin, outline=outline, width=2)
    draw.rectangle([cx - 16, 104, cx + 16, 145], fill=skin)

    if is_female:
        # Long hair for the female mannequin
        draw.ellipse([cx - 52, 4, cx + 52, 108], fill="#3b2a20")
        draw.ellipse([cx - 58, 48, cx - 25, 178], fill="#3b2a20")
        draw.ellipse([cx + 25, 48, cx + 58, 178], fill="#3b2a20")

        # Feminine torso: slightly narrower shoulders and defined waist
        draw.polygon(
            [
                (cx - 76, 160), (cx + 76, 160),
                (cx + 82, 235), (cx + 60, 315),
                (cx - 60, 315), (cx - 82, 235)
            ],
            fill=top_hex, outline=outline,
        )

        # Arms
        draw.polygon(
            [(cx - 76, 168), (cx - 122, 300), (cx - 101, 310), (cx - 58, 198)],
            fill=skin, outline=outline,
        )
        draw.polygon(
            [(cx + 76, 168), (cx + 122, 300), (cx + 101, 310), (cx + 58, 198)],
            fill=skin, outline=outline,
        )

        # Feminine waist and hips
        draw.polygon(
            [
                (cx - 60, 300), (cx + 60, 300),
                (cx + 88, 350), (cx + 82, 480),
                (cx - 82, 480), (cx - 88, 350)
            ],
            fill=bottom_hex, outline=outline,
        )

    else:
        # Short hair for the male mannequin
        draw.pieslice(
            [cx - 48, 8, cx + 48, 96],
            start=180, end=360, fill="#3b2a20"
        )

        # Male torso: broader shoulders
        draw.polygon(
            [(cx - 88, 168), (cx + 88, 168),
             (cx + 100, 310), (cx - 100, 310)],
            fill=top_hex, outline=outline,
        )

        # Arms
        draw.polygon(
            [(cx - 88, 168), (cx - 136, 300), (cx - 108, 312), (cx - 72, 188)],
            fill=skin, outline=outline,
        )
        draw.polygon(
            [(cx + 88, 168), (cx + 136, 300), (cx + 108, 312), (cx + 72, 188)],
            fill=skin, outline=outline,
        )

        # Male hips
        draw.polygon(
            [(cx - 94, 305), (cx + 94, 305),
             (cx + 84, 480), (cx - 84, 480)],
            fill=bottom_hex, outline=outline,
        )

    # --- Legs ---
    draw.line([(cx, 380), (cx, 480)], fill=(0, 0, 0, 40), width=3)
    draw.rectangle([cx - 84, 475, cx - 14, 575], fill=bottom_hex, outline=outline)
    draw.rectangle([cx + 14, 475, cx + 84, 575], fill=bottom_hex, outline=outline)

    # --- Shoes ---
    draw.rounded_rectangle(
        [cx - 90, 568, cx - 8, 610],
        radius=12, fill=shoes_hex, outline=outline
    )
    draw.rounded_rectangle(
        [cx + 8, 568, cx + 90, 610],
        radius=12, fill=shoes_hex, outline=outline
    )

    return img
