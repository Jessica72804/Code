# Pharmacy Inventory and Monitoring System

A lightweight FastAPI-based backend for managing drugs, suppliers, inventory, and sales with reporting endpoints.

## Features
- CRUD for Drugs and Suppliers
- Inventory items with batches, expiry, reorder thresholds
- Inventory transactions (purchases, sales, adjustments)
- Sales with line items and automatic inventory deduction
- Reports: low stock, sales summary, top selling

## Quickstart

1. Create virtual environment (optional) and install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python cli.py run --reload
```

API docs will be available at http://localhost:8000/docs

3. Seed sample data (optional):
```bash
python -m app.seed
```

## Configuration
- `DATABASE_URL`: defaults to `sqlite:///./pharmacy.db`.
- Set via environment or `.env` file.
