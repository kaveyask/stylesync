"""
seed_database.py
Run this once to populate StyleSync with sample wardrobe items so the app
has data to demo with.

Usage:
    python seed_database.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

import database as db
from colors import COLOR_HEX

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# type, name, color, occasion, gender
SAMPLE_ITEMS = [
    ("top", "White Casual Shirt", "white", "casual", "Male"),
    ("top", "Blue Denim Shirt", "blue", "casual", "Male"),
    ("top", "Black Formal Shirt", "black", "formal", "Male"),
    ("top", "Grey Sports Tee", "grey", "sport", "Unisex"),
    ("top", "Pink Blouse", "pink", "casual", "Female"),
    ("top", "Purple Party Top", "purple", "party", "Female"),
    ("bottom", "Black Jeans", "black", "casual", "Unisex"),
    ("bottom", "Beige Chinos", "beige", "formal", "Male"),
    ("bottom", "Navy Track Pants", "navy", "sport", "Unisex"),
    ("bottom", "Grey Jeans", "grey", "casual", "Female"),
    ("shoes", "White Sneakers", "white", "casual", "Unisex"),
    ("shoes", "Black Formal Shoes", "black", "formal", "Male"),
    ("shoes", "Grey Running Shoes", "grey", "sport", "Unisex"),
    ("shoes", "Brown Loafers", "brown", "formal", "Male"),
    ("shoes", "Pink Heels", "pink", "party", "Female"),
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

    draw.text((30, 260), name, fill="#666666", font=font)
    img.save(path)


def main():
    db.init_db()
    print("Generating placeholder images...")
    for type_, name, color, occasion, gender in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(UPLOAD_DIR, filename)
        make_placeholder_image(name, color, path)

    print("Inserting sample items into the database...")
    for type_, name, color, occasion, gender in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(UPLOAD_DIR, filename)
        db.add_item(type_, name, color, occasion, gender, path)

    print(f"Done! Inserted {len(SAMPLE_ITEMS)} sample wardrobe items.")


if __name__ == "__main__":
    main()
