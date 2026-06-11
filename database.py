import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "")


class PgConnection:
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()

    def execute(self, sql, params=None):
        self._cur.execute(sql, params or ())
        return self._cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._cur.close()
        self._conn.close()


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return PgConnection(conn)


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_approved INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            group_name TEXT NOT NULL,
            flag_emoji TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            home_team_id INTEGER NOT NULL REFERENCES teams(id),
            away_team_id INTEGER NOT NULL REFERENCES teams(id),
            match_date TEXT NOT NULL,
            match_time TEXT DEFAULT '00:00',
            stage TEXT NOT NULL DEFAULT 'group',
            group_name TEXT DEFAULT '',
            home_score INTEGER DEFAULT NULL,
            away_score INTEGER DEFAULT NULL,
            is_finished INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            match_id INTEGER NOT NULL REFERENCES matches(id),
            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,
            points_earned INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, match_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bonus_predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            category TEXT NOT NULL,
            value TEXT NOT NULL,
            points_earned INTEGER DEFAULT NULL,
            UNIQUE(user_id, category)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bonus_results (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL
        )
    """)

    existing_cols = [r["column_name"] for r in conn.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'public'"
    ).fetchall()]
    if "email" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT '' NOT NULL")
    if "password_hash" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT '' NOT NULL")
    if "is_admin" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    conn.commit()
    conn.close()
