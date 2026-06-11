import sqlite3
import os

IS_VERCEL = os.environ.get("VERCEL") == "1"
DB_PATH = "/tmp/bolao.db" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "bolao.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            group_name TEXT NOT NULL,
            flag_emoji TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team_id INTEGER NOT NULL REFERENCES teams(id),
            away_team_id INTEGER NOT NULL REFERENCES teams(id),
            match_date TEXT NOT NULL,
            match_time TEXT DEFAULT '00:00',
            stage TEXT NOT NULL DEFAULT 'group',
            group_name TEXT DEFAULT '',
            home_score INTEGER DEFAULT NULL,
            away_score INTEGER DEFAULT NULL,
            is_finished INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            match_id INTEGER NOT NULL REFERENCES matches(id),
            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,
            points_earned INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, match_id)
        );

        CREATE TABLE IF NOT EXISTS bonus_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            category TEXT NOT NULL,
            value TEXT NOT NULL,
            points_earned INTEGER DEFAULT NULL,
            UNIQUE(user_id, category)
        );

        CREATE TABLE IF NOT EXISTS bonus_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
