import os
import sqlite3
from datetime import datetime


DB_PATH = os.environ.get(
    "PHARMACY_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "pharmacy.db"),
)
DB_PATH = os.path.abspath(DB_PATH)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sku TEXT UNIQUE,
            unit TEXT,
            low_stock_threshold INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            supplier_id INTEGER,
            lot_number TEXT,
            expiry_date TEXT NOT NULL, -- YYYY-MM-DD
            quantity_received INTEGER NOT NULL,
            quantity_remaining INTEGER NOT NULL,
            unit_cost REAL,
            received_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sold_at TEXT NOT NULL DEFAULT (datetime('now')),
            total REAL
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            batch_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price REAL,
            FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(batch_id) REFERENCES batches(id) ON DELETE SET NULL
        );
        """
    )

    connection.commit()
    connection.close()


def upsert_supplier(connection: sqlite3.Connection, name: str, contact: str | None = None) -> int:
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM suppliers WHERE name = ?", (name.strip(),))
    row = cursor.fetchone()
    if row:
        return int(row["id"])
    cursor.execute(
        "INSERT INTO suppliers(name, contact) VALUES (?, ?)", (name.strip(), contact)
    )
    connection.commit()
    return int(cursor.lastrowid)
