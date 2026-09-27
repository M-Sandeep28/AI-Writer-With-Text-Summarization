"""
Database management module for AI Writer with Text Summarization.
Handles SQLite initialization, user storage, summary history, and user stats.
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any

DB_FILE = "app.db"


def get_connection():
    """Establish connection to SQLite database with Row factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initialize SQLite database tables if they do not exist.
    Tables: users, summaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            original_text TEXT NOT NULL,
            generated_summary TEXT NOT NULL,
            original_word_count INTEGER NOT NULL,
            summary_word_count INTEGER NOT NULL,
            compression_percentage REAL NOT NULL,
            summary_length TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


def create_user(name: str, email: str, password_hash: str) -> Optional[int]:
    """
    Create a new user record in the database.
    Returns user ID on success, or None if email already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        # Email already exists
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user dictionary by email."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE LOWER(email) = ?",
        (email.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user dictionary by user ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def update_user_name(user_id: int, new_name: str) -> bool:
    """Update user's display name."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET name = ? WHERE id = ?",
        (new_name.strip(), user_id)
    )
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def create_summary(
    user_id: int,
    title: str,
    original_text: str,
    generated_summary: str,
    original_word_count: int,
    summary_word_count: int,
    compression_percentage: float,
    summary_length: str
) -> int:
    """
    Save a new summary record associated with a specific user.
    Returns the newly created summary ID.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO summaries (
            user_id, title, original_text, generated_summary,
            original_word_count, summary_word_count,
            compression_percentage, summary_length
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id, title.strip(), original_text, generated_summary,
            original_word_count, summary_word_count,
            round(compression_percentage, 2), summary_length
        )
    )
    conn.commit()
    summary_id = cursor.lastrowid
    conn.close()
    return summary_id


def get_user_summaries(user_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all summary records belonging to a user, sorted newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, title, original_text, generated_summary,
               original_word_count, summary_word_count, compression_percentage,
               summary_length, created_at
        FROM summaries
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_summary_by_id(summary_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single summary record, verifying user ownership.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, title, original_text, generated_summary,
               original_word_count, summary_word_count, compression_percentage,
               summary_length, created_at
        FROM summaries
        WHERE id = ? AND user_id = ?
        """,
        (summary_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def delete_summary(summary_id: int, user_id: int) -> bool:
    """
    Delete a specific summary record owned by the user.
    Returns True if deleted, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM summaries WHERE id = ? AND user_id = ?",
        (summary_id, user_id)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    Calculate user metrics: total summaries, total original words processed, latest date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_summaries,
            COALESCE(SUM(original_word_count), 0) as total_words_processed,
            MAX(created_at) as latest_summary_date
        FROM summaries
        WHERE user_id = ?
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return {
        "total_summaries": 0,
        "total_words_processed": 0,
        "latest_summary_date": None
    }
