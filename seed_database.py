"""
seed_database.py
Run this once after creating the schema (schema.sql) to populate
StyleSync with sample wardrobe items so the app has data to demo with.

Usage:
    python seed_database.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

import database as db
from silhouette import COLOR_HEX

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# type, name, color, occasion
SAMPLE_ITEMS = [
    ("top", "White Casual Shirt", "white", "casual"),
    ("top", "Blue Denim Shirt", "blue", "casual"),
    ("top", "Black Formal Shirt", "black", "formal"),
    ("top", "Grey Sports Tee", "grey", "sport"),
    ("bottom", "Black Jeans", "black", "casual"),
    ("bottom", "Beige Chinos", "beige", "formal"),
    ("bottom", "Navy Track Pants", "navy", "sport"),
    ("bottom", "Grey Jeans", "grey", "casual"),
    ("shoes", "White Sneakers", "white", "casual"),
    ("shoes", "Black Formal Shoes", "black", "formal"),
    ("shoes", "Grey Running Shoes", "grey", "sport"),
    ("shoes", "Brown Loafers", "brown", "formal"),
]


def make_placeholder_image(name, color, path):
    """Creates a simple rounded-rectangle swatch image labeled with the item name."""
    hex_color = COLOR_HEX.get(color, "#CCCCCC")
    img = Image.new("RGB", (300, 300), "white")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([20, 20, 280, 280], radius=24, fill=hex_color, outline="#dddddd", width=2)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    text = name
    text_color = "#111111" if hex_color.lower() in ("#f5f5f5", "#d8c3a5", "#eab308") else "#ffffff"
    draw.text((30, 260), text, fill="#666666", font=font)
    img.save(path)


def main():
    db.init_db()
    print("Generating placeholder images...")
    for type_, name, color, occasion in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(UPLOAD_DIR, filename)
        make_placeholder_image(name, color, path)

    print("Inserting sample items into MySQL...")
    for type_, name, color, occasion in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(UPLOAD_DIR, filename)
        db.add_item(type_, name, color, occasion, path)

    print(f"Done! Inserted {len(SAMPLE_ITEMS)} sample wardrobe items.")


if __name__ == "__main__":
    main()
