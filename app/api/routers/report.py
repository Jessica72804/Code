from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta

from app.api.deps import get_db
from app.models import InventoryItem, Drug, Sale, SaleItem

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)):
    rows = db.execute(
        select(InventoryItem, Drug).join(Drug, InventoryItem.drug_id == Drug.id).where(
            InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
        )
    ).all()
    return [
        {
            "drug_id": d.id,
            "drug_name": d.name,
            "quantity_on_hand": i.quantity_on_hand,
            "reorder_level": i.reorder_level,
        }
        for (i, d) in rows
    ]


@router.get("/sales-summary")
def sales_summary(days: int = 30, db: Session = Depends(get_db)):
    start_date = date.today() - timedelta(days=days)
    rows = db.execute(
        select(
            func.sum(Sale.subtotal),
            func.sum(Sale.tax_total),
            func.sum(Sale.total),
        ).where(Sale.sale_date >= start_date)
    ).first()
    subtotal, tax_total, total = rows if rows else (0.0, 0.0, 0.0)
    return {"subtotal": float(subtotal or 0), "tax_total": float(tax_total or 0), "total": float(total or 0)}


@router.get("/top-selling")
def top_selling(limit: int = 10, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Drug.name, func.sum(SaleItem.quantity).label("qty")).join(Drug, Drug.id == SaleItem.drug_id).group_by(Drug.name).order_by(func.sum(SaleItem.quantity).desc()).limit(limit)
    ).all()
    return [{"drug_name": name, "quantity": int(qty)} for name, qty in rows]
