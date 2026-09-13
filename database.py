"""
database.py
All database access for StyleSync lives here.
Uses SQLite -- a single local file, no separate database server needed.
This makes the app work anywhere, including free cloud hosting.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wardrobe.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates tables if they don't already exist. Safe to call every startup."""
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
            date_worn   DATE NOT NULL,
            FOREIGN KEY (top_id)    REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (bottom_id) REFERENCES clothes(id) ON DELETE SET NULL,
            FOREIGN KEY (shoes_id)  REFERENCES clothes(id) ON DELETE SET NULL
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def add_item(type_, name, color, occasion, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clothes (type, name, color, occasion, image_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (type_, name, color, occasion, image_path),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_items(type_=None):
    conn = get_connection()
    cur = conn.cursor()
    if type_:
        cur.execute("SELECT * FROM clothes WHERE type=? ORDER BY id", (type_,))
    else:
        cur.execute("SELECT * FROM clothes ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clothes WHERE id=?", (item_id,))
    conn.commit()
    cur.close()
    conn.close()


def log_outfit(top_id, bottom_id, shoes_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO outfit_log (top_id, bottom_id, shoes_id, date_worn) "
        "VALUES (?, ?, ?, DATE('now'))",
        (top_id, bottom_id, shoes_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_recent_outfit_ids(days=5):
    """Returns a set of (top_id, bottom_id, shoes_id) tuples worn in the last `days` days."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT top_id, bottom_id, shoes_id FROM outfit_log "
        "WHERE date_worn >= DATE('now', ? )",
        (f"-{days} days",),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {(r["top_id"], r["bottom_id"], r["shoes_id"]) for r in rows}


def get_stats():
    """Returns (total_items, outfits_worn_this_week, last_worn_date)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM clothes")
    total_items = cur.fetchone()["total"]

    cur.execute(
        "SELECT COUNT(*) AS total FROM outfit_log "
        "WHERE date_worn >= DATE('now', '-7 days')"
    )
    week_outfits = cur.fetchone()["total"]

    cur.execute("SELECT date_worn FROM outfit_log ORDER BY date_worn DESC LIMIT 1")
    last_row = cur.fetchone()

    cur.close()
    conn.close()
    return total_items, week_outfits, (last_row["date_worn"] if last_row else None)
