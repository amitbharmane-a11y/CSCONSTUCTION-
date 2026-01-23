from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .settings import settings

# Global variable to track database type
IS_POSTGRESQL = False
POSTGRES_CONNECTION = None

def get_connection():
    """Get database connection - supports both SQLite and PostgreSQL"""
    global IS_POSTGRESQL, POSTGRES_CONNECTION

    # Check if we have DATABASE_URL for PostgreSQL (Vercel)
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql"):
        if not IS_POSTGRESQL:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                POSTGRES_CONNECTION = psycopg2.connect(database_url)
                IS_POSTGRESQL = True
            except ImportError:
                print("psycopg2 not available, falling back to SQLite")
                IS_POSTGRESQL = False

        if IS_POSTGRESQL and POSTGRES_CONNECTION:
            return POSTGRES_CONNECTION

    # Default to SQLite for local development
    IS_POSTGRESQL = False
    _ensure_db_dir()
    conn = sqlite3.connect(settings.database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _ensure_db_dir() -> None:
    db_path = Path(settings.database_path)
    if db_path.parent and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        if IS_POSTGRESQL:
            # PostgreSQL uses different cursor
            cur = conn.cursor()
        else:
            # SQLite cursor
            cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        if not IS_POSTGRESQL:
            conn.close()


def init_db() -> None:
    """Initialize database schema"""
    global IS_POSTGRESQL

    if IS_POSTGRESQL:
        # For PostgreSQL, we'll need different schema
        print("PostgreSQL database - schema initialization may be needed")
        return

    # SQLite schema initialization
    _ensure_db_dir()
    with db_cursor() as cur:
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              client TEXT NOT NULL,
              location TEXT NOT NULL,
              contract_no TEXT,
              start_date TEXT,
              end_date TEXT,
              total_contract_value REAL,
              profit_margin_target REAL DEFAULT 10.0,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS daily_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              log_date TEXT NOT NULL,
              weather TEXT,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS daily_activities (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              daily_log_id INTEGER NOT NULL,
              category TEXT NOT NULL,
              activity TEXT NOT NULL,
              uom TEXT NOT NULL,
              quantity REAL NOT NULL DEFAULT 0,
              labour_count INTEGER NOT NULL DEFAULT 0,
              machinery TEXT,
              notes TEXT,
              FOREIGN KEY(daily_log_id) REFERENCES daily_logs(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS cost_entries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              entry_date TEXT NOT NULL,
              cost_head TEXT NOT NULL,
              description TEXT NOT NULL,
              vendor TEXT,
              amount REAL NOT NULL,
              quantity REAL,
              uom TEXT,
              unit_rate REAL,
              payment_mode TEXT,
              bill_no TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS budget_items (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              cost_head TEXT NOT NULL,
              budget_amount REAL NOT NULL,
              notes TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              UNIQUE(project_id, cost_head),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )


def seed_if_empty() -> None:
    """Seed database with sample data if empty"""
    with db_cursor() as cur:
        if IS_POSTGRESQL:
            cur.execute("SELECT COUNT(*) AS c FROM projects;")
            count = int(cur.fetchone()[0])
        else:
            cur.execute("SELECT COUNT(*) AS c FROM projects;")
            count = int(cur.fetchone()["c"])

        if count > 0:
            return

        # Insert sample project
        if IS_POSTGRESQL:
            cur.execute(
                """
                INSERT INTO projects (name, client, location, contract_no, start_date, end_date, total_contract_value, profit_margin_target)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    "Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
                    "Indian Railways / PWD",
                    "Maharashtra",
                    "PWD-IR-ROB-001",
                    "2026-01-01",
                    "2026-12-31",
                    10_00_00_000,  # 10 crores total contract value
                    12.0,  # 12% profit margin target
                ),
            )
            project_id = cur.fetchone()[0]
        else:
            cur.execute(
                """
                INSERT INTO projects (name, client, location, contract_no, start_date, end_date, total_contract_value, profit_margin_target)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
                    "Indian Railways / PWD",
                    "Maharashtra",
                    "PWD-IR-ROB-001",
                    "2026-01-01",
                    "2026-12-31",
                    10_00_00_000,  # 10 crores total contract value
                    12.0,  # 12% profit margin target
                ),
            )
            project_id = cur.lastrowid

        print(f"Database seeded with sample project ID: {project_id}")