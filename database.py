"""
database.py - Data persistence module.

Manages the SQLite database connection and the initialization
of the table structure for the Production Order System.
"""

import sqlite3

DB_NAME = 'orders.db'
"""str: Path to the SQLite database file."""

def get_connection():
    """
    Creates and returns a connection to the SQLite database.

    Configures row_factory to allow accessing results by column name 
    (e.g., row['product']) instead of by index.

    Returns:
        sqlite3.Connection: Active database connection object.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_dataBase():
    """
    Initializes the database.

    Creates the 'orders' table if it does not exist with the following schema:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - product: TEXT NOT NULL
    - quantity: INTEGER NOT NULL
    - status: TEXT (Default: 'Pending')
    - created_at: TEXT (Automatic timestamp)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")