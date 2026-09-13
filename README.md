# StyleSync – Intelligent Wardrobe & Outfit Matching System

A Python + Streamlit + MySQL app that stores your wardrobe, matches outfits
using color/occasion rules, and shows the result on a customizable silhouette.

## File structure

```
StyleSync/
├── app.py              # Streamlit UI (run this)
├── database.py         # MySQL connection + queries
├── outfit_logic.py      # Color/occasion matching rules
├── silhouette.py        # Draws the human figure + outfit with Pillow
├── seed_database.py     # One-time script: sample items + placeholder images
├── schema.sql            # MySQL table creation
├── requirements.txt
├── uploads/              # Clothing photos land here (auto-created)
└── README.md
```

## Setup steps

1. **Install MySQL** if you don't already have it running, and make sure the
   server is started.

2. **Create the database and tables.** Open a terminal in this folder and run:
   ```
   mysql -u root -p < schema.sql
   ```
   Enter your MySQL root password when prompted.

3. **Set your credentials.** Open `database.py` and edit the `DB_CONFIG`
   dictionary near the top — put in your real MySQL username/password.

4. **Install Python dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Seed sample data** (optional but recommended so the app isn't empty on
   first run):
   ```
   python seed_database.py
   ```
   This generates 12 placeholder clothing images and inserts them into MySQL.

6. **Run the app:**
   ```
   streamlit run app.py
   ```
   It opens automatically at `http://localhost:8501`.

## Using the app

- **Dashboard** — quick stats: total items, outfits worn this week.
- **Add Item** — upload a photo, pick type/color/occasion, save to MySQL.
- **My Wardrobe** — browse and delete stored items.
- **Suggest Outfit** — pick a skin tone + occasion, get a matched outfit shown
  on a silhouette; click "Wear this today" to log it (keeps it from repeating
  for a few days).

## Notes for your report/demo

- All matching is rule-based (color-compatibility dictionary + occasion
  filter) — no AI/ML involved, keeping it in scope for a "basic Python"
  course project.
- The silhouette is drawn entirely with Pillow shapes (`ImageDraw`), colored
  from the matched items and the chosen skin tone — no image generation APIs.
- Swap `seed_database.py`'s sample list for your own wardrobe any time, or
  just add items through the **Add Item** tab.
