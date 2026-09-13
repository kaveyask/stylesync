# StyleSync – Wardrobe & Outfit Matching System

A Python + Streamlit + SQLite app that stores your wardrobe, matches outfits
using color/occasion rules, scores each outfit with a deterministic
**Match Score**, and keeps suggestions, stats, and history **separate for
Male and Female** wardrobes. There is no AI/model call anywhere in this
app — no avatar, no "doll", no image generation. Everything is your real
garment photos plus rule-based Python.

**Every wardrobe is private.** The app opens on a Login / Sign Up screen.
Each account only ever sees, adds to, and gets outfit suggestions from its
own clothes — one user can never see or modify another user's wardrobe,
even if they share the same running app.

## File structure

```
StyleSync/
├── app.py              # Streamlit UI (run this)
├── database.py         # SQLite connection + queries (all scoped by user_id)
├── outfit_logic.py      # Color/occasion matching rules + Match Score
├── colors.py             # Color swatch palette + gender constants
├── auth.py                # Password hashing (PBKDF2, stdlib only)
├── seed_database.py     # One-time script: demo account + sample items
├── requirements.txt
├── uploads/<user_id>/     # Each user's clothing photos, kept separate
└── README.md
```

## Setup steps

1. **Install Python dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Seed sample data** (optional but recommended so the app isn't empty on
   first run):
   ```
   python seed_database.py
   ```
   This creates a demo account (`[email protected]` / `demo1234`), generates
   placeholder clothing images (tagged Male / Female / Unisex), and inserts
   them into `wardrobe.db`, a local SQLite file created automatically the
   first time you run the app.

3. **Run the app:**
   ```
   streamlit run app.py
   ```
   It opens automatically at `http://localhost:8501`. Log in with the demo
   account above, or use **Sign Up** to create your own — your wardrobe is
   tied to that account and no one else can see it.

## Using the app

- **Log In / Sign Up** — the first screen. Passwords are hashed (PBKDF2,
  100,000 iterations, random per-user salt) before being stored — never
  saved in plain text.
- **Dashboard** — Male and Female tabs, each with its own wardrobe size,
  looks worn this week, average Match Score, last look, and a wear-history
  calendar heatmap (like a GitHub contribution graph) for that gender.
- **Add Item** — upload a real photo, pick type/color/occasion/gender, save
  to the database.
- **My Wardrobe** — browse, filter by type and gender, and delete stored
  items.
- **Style Me** — pick a wardrobe (Male/Female) and occasion, get a matched
  outfit shown as a flat-lay of your real garment photos (no avatar), with
  an animated Match Score meter. "Try Another" re-rolls, "♡ Save to
  Favorites" pins it, "✓ Wear This Today" logs it (keeps it from repeating
  for a few days and feeds the calendar heatmap).
- **Favorites** — saved looks per gender, ready to re-wear or remove.

## Notes for your report/demo

- All matching is rule-based (color-compatibility dictionary + occasion
  filter) — no AI/ML involved.
- The **Match Score** is a deterministic weighted formula: it scores each
  pairwise color match (with a bonus for "editor's pick" pairings like
  black/white or navy/beige) and adds a small freshness bonus for outfits
  you haven't worn recently. See `outfit_logic.calculate_match_score`.
- Items tagged **Unisex** are eligible for both the Male and Female
  wardrobe when generating suggestions and stats.
- Swap `seed_database.py`'s sample list for your own wardrobe any time, or
  just add items through the **Add Item** tab.
