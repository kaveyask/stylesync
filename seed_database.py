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
import auth
from colors import COLOR_HEX

DEMO_EMAIL = "[email protected]"
DEMO_PASSWORD = "demo1234"

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


def get_or_create_demo_user():
    user = db.get_user_by_email(DEMO_EMAIL)
    if user:
        return user["id"]
    password_hash, salt = auth.hash_password(DEMO_PASSWORD)
    return db.create_user(DEMO_EMAIL, password_hash, salt)


def main():
    db.init_db()
    user_id = get_or_create_demo_user()
    upload_dir = os.path.join("uploads", str(user_id))
    os.makedirs(upload_dir, exist_ok=True)

    print("Generating placeholder images...")
    for type_, name, color, occasion, gender in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(upload_dir, filename)
        make_placeholder_image(name, color, path)

    print("Inserting sample items into the database...")
    for type_, name, color, occasion, gender in SAMPLE_ITEMS:
        filename = name.lower().replace(" ", "_") + ".png"
        path = os.path.join(upload_dir, filename)
        db.add_item(user_id, type_, name, color, occasion, gender, path)

    print(f"Done! Inserted {len(SAMPLE_ITEMS)} sample wardrobe items.")
    print(f"Log in with: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
