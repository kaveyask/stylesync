"""
database.py
All database access for StyleSync lives here.
Uses SQLite -- a single local file, no separate database server needed.

Schema additions in this version:
- clothes.gender          ("Male" / "Female" / "Unisex")
- outfit_log.gender        which wardrobe the logged outfit came from
- outfit_log.match_score   rule-based compatibility score (0-100) at log time
- favorites                pinned outfits the user can re-wear instantly
"""

import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wardrobe.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_names(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return {row["name"] for row in cur.fetchall()}


def init_db():
    """Creates tables if they don't already exist and migrates older DBs
    (adds new columns) in-place. Safe to call every startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clothes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL,
            name        TEXT NOT NULL,
            color       TEXT NOT NULL,
            occasion    TEXT NOT NULL,
            gender      TEXT NOT NULL DEFAULT 'Unisex',
            image_path  TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS outfit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            top_id      INTEGER,
            bottom_id   INTEGER,
            shoes_id    INTEGER,
            gender      TEXT NOT NULL DEFAULT 'Unisex',
            match_score INTEGER,
            date_worn   DATE NOT NULL,
            FOREIGN KEY (top_id)    REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (bottom_id) REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (shoes_id)  REFERENCES clothes(id) ON DELETE SET NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            top_id      INTEGER,
            bottom_id   INTEGER,
            shoes_id    INTEGER,
            gender      TEXT NOT NULL DEFAULT 'Unisex',
            match_score INTEGER,
            saved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (top_id)    REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (bottom_id) REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (shoes_id)  REFERENCES clothes(id) ON DELETE SET NULL
        )
        """
    )

    # --- migrations for DBs created before this version ---
    clothes_cols = _column_names(cur, "clothes")
    if "gender" not in clothes_cols:
        cur.execute("ALTER TABLE clothes ADD COLUMN gender TEXT NOT NULL DEFAULT 'Unisex'")

    log_cols = _column_names(cur, "outfit_log")
    if "gender" not in log_cols:
        cur.execute("ALTER TABLE outfit_log ADD COLUMN gender TEXT NOT NULL DEFAULT 'Unisex'")
    if "match_score" not in log_cols:
        cur.execute("ALTER TABLE outfit_log ADD COLUMN match_score INTEGER")

    conn.commit()
    cur.close()
    conn.close()


# ------------------------------------------------------------------
# Clothes
# ------------------------------------------------------------------
def add_item(type_, name, color, occasion, gender, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clothes (type, name, color, occasion, gender, image_path) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (type_, name, color, occasion, gender, image_path),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_items(type_=None, gender=None):
    """gender=None returns everything. gender='Male'/'Female' also includes
    'Unisex' items, since those fit either wardrobe."""
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM clothes WHERE 1=1"
    params = []

    if type_:
        query += " AND type=?"
        params.append(type_)

    if gender:
        query += " AND (gender=? OR gender='Unisex')"
        params.append(gender)

    query += " ORDER BY id"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_item_by_id(item_id):
    if item_id is None:
        return None
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clothes WHERE id=?", (item_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clothes WHERE id=?", (item_id,))
    conn.commit()
    cur.close()
    conn.close()


# ------------------------------------------------------------------
# Outfit log (wear history)
# ------------------------------------------------------------------
def log_outfit(top_id, bottom_id, shoes_id, gender, match_score=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO outfit_log (top_id, bottom_id, shoes_id, gender, match_score, date_worn) "
        "VALUES (?, ?, ?, ?, ?, DATE('now'))",
        (top_id, bottom_id, shoes_id, gender, match_score),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_recent_outfit_ids(gender=None, days=5):
    """Returns a set of (top_id, bottom_id, shoes_id) tuples worn in the last
    `days` days, optionally scoped to one gender's wardrobe."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT top_id, bottom_id, shoes_id FROM outfit_log WHERE date_worn >= DATE('now', ?)"
    params = [f"-{days} days"]
    if gender:
        query += " AND gender=?"
        params.append(gender)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {(r["top_id"], r["bottom_id"], r["shoes_id"]) for r in rows}


def get_stats(gender=None):
    """Returns (total_items, outfits_worn_this_week, last_worn_date, avg_score)
    optionally scoped to one gender's wardrobe."""
    conn = get_connection()
    cur = conn.cursor()

    if gender:
        cur.execute(
            "SELECT COUNT(*) AS total FROM clothes WHERE gender=? OR gender='Unisex'",
            (gender,),
        )
    else:
        cur.execute("SELECT COUNT(*) AS total FROM clothes")
    total_items = cur.fetchone()["total"]

    week_query = "SELECT COUNT(*) AS total FROM outfit_log WHERE date_worn >= DATE('now', '-7 days')"
    score_query = "SELECT AVG(match_score) AS avg_score FROM outfit_log WHERE match_score IS NOT NULL"
    last_query = "SELECT date_worn FROM outfit_log"
    params = []
    if gender:
        week_query += " AND gender=?"
        score_query += " AND gender=?"
        last_query += " WHERE gender=?"
        params.append(gender)
    last_query += " ORDER BY date_worn DESC LIMIT 1"

    cur.execute(week_query, params)
    week_outfits = cur.fetchone()["total"]

    cur.execute(score_query, params)
    avg_row = cur.fetchone()["avg_score"]
    avg_score = round(avg_row) if avg_row is not None else None

    cur.execute(last_query, params)
    last_row = cur.fetchone()

    cur.close()
    conn.close()
    return total_items, week_outfits, (last_row["date_worn"] if last_row else None), avg_score


def get_wear_history(gender, weeks=12):
    """Returns a list of (date, score_or_None) for each day in the last
    `weeks` weeks, most recent last. score is the highest match_score logged
    that day (None if nothing was worn). Used for the calendar heatmap."""
    conn = get_connection()
    cur = conn.cursor()
    days = weeks * 7
    start = date.today() - timedelta(days=days - 1)

    cur.execute(
        "SELECT date_worn, MAX(match_score) AS score FROM outfit_log "
        "WHERE gender=? AND date_worn >= ? GROUP BY date_worn",
        (gender, start.isoformat()),
    )
    by_day = {row["date_worn"]: row["score"] for row in cur.fetchall()}
    cur.close()
    conn.close()

    history = []
    for i in range(days):
        d = start + timedelta(days=i)
        history.append((d, by_day.get(d.isoformat())))
    return history


# ------------------------------------------------------------------
# Favorites
# ------------------------------------------------------------------
def add_favorite(top_id, bottom_id, shoes_id, gender, match_score=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO favorites (top_id, bottom_id, shoes_id, gender, match_score) "
        "VALUES (?, ?, ?, ?, ?)",
        (top_id, bottom_id, shoes_id, gender, match_score),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_favorites(gender=None):
    conn = get_connection()
    cur = conn.cursor()
    if gender:
        cur.execute(
            "SELECT * FROM favorites WHERE gender=? ORDER BY saved_at DESC", (gender,)
        )
    else:
        cur.execute("SELECT * FROM favorites ORDER BY saved_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def delete_favorite(favorite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE id=?", (favorite_id,))
    conn.commit()
    cur.close()
    conn.close()
