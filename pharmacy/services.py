from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .db import get_connection, init_db, upsert_supplier


# Product operations

def add_product(name: str, sku: Optional[str], unit: Optional[str], low_stock_threshold: int) -> int:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO products(name, sku, unit, low_stock_threshold) VALUES (?, ?, ?, ?)",
        (name.strip(), sku.strip() if sku else None, unit.strip() if unit else None, int(low_stock_threshold)),
    )
    connection.commit()
    product_id = int(cursor.lastrowid)
    connection.close()
    return product_id


def list_products_with_stock() -> List[sqlite3.Row]:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT p.*, COALESCE(SUM(b.quantity_remaining), 0) AS stock_on_hand
        FROM products p
        LEFT JOIN batches b ON b.product_id = p.id
        GROUP BY p.id
        ORDER BY p.name ASC
        """
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


# Receiving operations

def receive_stock(
    product_id: int,
    quantity: int,
    expiry_date: str,
    supplier_name: Optional[str] = None,
    lot_number: Optional[str] = None,
    unit_cost: Optional[float] = None,
) -> int:
    connection = get_connection()
    cursor = connection.cursor()

    supplier_id: Optional[int] = None
    if supplier_name:
        supplier_id = upsert_supplier(connection, supplier_name)

    cursor.execute(
        """
        INSERT INTO batches(product_id, supplier_id, lot_number, expiry_date, quantity_received, quantity_remaining, unit_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(product_id),
            supplier_id,
            lot_number.strip() if lot_number else None,
            expiry_date.strip(),
            int(quantity),
            int(quantity),
            float(unit_cost) if unit_cost is not None else None,
        ),
    )
    connection.commit()
    batch_id = int(cursor.lastrowid)
    connection.close()
    return batch_id


# Selling operations with FEFO (First-Expire-First-Out)

def sell_product(product_id: int, quantity: int, unit_price: Optional[float] = None) -> Tuple[int, int]:
    remaining = int(quantity)
    connection = get_connection()
    cursor = connection.cursor()

    # Create sale record
    cursor.execute("INSERT INTO sales(total) VALUES (NULL)")
    sale_id = int(cursor.lastrowid)

    # Fetch batches ordered by earliest expiry first
    cursor.execute(
        """
        SELECT id, quantity_remaining FROM batches
        WHERE product_id = ? AND quantity_remaining > 0
        ORDER BY date(expiry_date) ASC, id ASC
        """,
        (int(product_id),),
    )
    batches = cursor.fetchall()

    for batch in batches:
        if remaining <= 0:
            break
        batch_id = int(batch["id"]) if "id" in batch.keys() else int(batch[0])
        qty_avail = int(batch["quantity_remaining"]) if "quantity_remaining" in batch.keys() else int(batch[1])
        allocate = min(remaining, qty_avail)
        if allocate <= 0:
            continue
        # Create sale item
        cursor.execute(
            "INSERT INTO sale_items(sale_id, product_id, batch_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
            (sale_id, int(product_id), batch_id, allocate, unit_price),
        )
        # Decrement batch remaining
        cursor.execute(
            "UPDATE batches SET quantity_remaining = quantity_remaining - ? WHERE id = ?",
            (allocate, batch_id),
        )
        remaining -= allocate

    # Compute total
    cursor.execute(
        "SELECT COALESCE(SUM(quantity * COALESCE(unit_price, 0)), 0) FROM sale_items WHERE sale_id = ?",
        (sale_id,),
    )
    total = float(cursor.fetchone()[0])
    cursor.execute("UPDATE sales SET total = ? WHERE id = ?", (total, sale_id))

    connection.commit()
    connection.close()

    # remaining is unsatisfied quantity
    return sale_id, remaining


# Alerts and reports

def get_alerts(days_until_expiry: int = 30) -> Dict[str, List[sqlite3.Row]]:
    today = date.today()
    near_date = today + timedelta(days=days_until_expiry)

    connection = get_connection()
    cursor = connection.cursor()

    # Low stock
    cursor.execute(
        """
        SELECT p.*, COALESCE(SUM(b.quantity_remaining), 0) AS stock_on_hand
        FROM products p
        LEFT JOIN batches b ON b.product_id = p.id
        GROUP BY p.id
        HAVING stock_on_hand <= p.low_stock_threshold
        ORDER BY stock_on_hand ASC
        """
    )
    low_stock = cursor.fetchall()

    # Near expiry
    cursor.execute(
        """
        SELECT b.*, p.name AS product_name
        FROM batches b
        JOIN products p ON p.id = b.product_id
        WHERE b.quantity_remaining > 0 AND date(b.expiry_date) BETWEEN date(?) AND date(?)
        ORDER BY date(b.expiry_date) ASC
        """,
        (today.isoformat(), near_date.isoformat()),
    )
    near_expiry = cursor.fetchall()

    # Expired
    cursor.execute(
        """
        SELECT b.*, p.name AS product_name
        FROM batches b
        JOIN products p ON p.id = b.product_id
        WHERE b.quantity_remaining > 0 AND date(b.expiry_date) < date(?)
        ORDER BY date(b.expiry_date) ASC
        """,
        (today.isoformat(),),
    )
    expired = cursor.fetchall()

    connection.close()

    return {"low_stock": low_stock, "near_expiry": near_expiry, "expired": expired}


def list_batches(product_id: Optional[int] = None) -> List[sqlite3.Row]:
    connection = get_connection()
    cursor = connection.cursor()
    if product_id:
        cursor.execute(
            """
            SELECT b.*, p.name AS product_name
            FROM batches b JOIN products p ON p.id = b.product_id
            WHERE b.product_id = ?
            ORDER BY date(b.expiry_date) ASC
            """,
            (int(product_id),),
        )
    else:
        cursor.execute(
            """
            SELECT b.*, p.name AS product_name
            FROM batches b JOIN products p ON p.id = b.product_id
            ORDER BY date(b.expiry_date) ASC
            """
        )
    rows = cursor.fetchall()
    connection.close()
    return rows


def sales_report(start_date: str, end_date: str) -> List[sqlite3.Row]:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT si.id, s.sold_at, p.name AS product_name, si.quantity, si.unit_price, si.batch_id
        FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        JOIN products p ON p.id = si.product_id
        WHERE date(s.sold_at) BETWEEN date(?) AND date(?)
        ORDER BY s.sold_at ASC
        """,
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


def list_all_products() -> List[sqlite3.Row]:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    connection.close()
    return rows
