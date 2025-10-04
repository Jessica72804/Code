from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.models import Sale, SaleItem, Drug, InventoryItem
from app.schemas import SaleCreate


class SaleService:
    @staticmethod
    def list_sales(db: Session, skip: int = 0, limit: int = 50) -> List[Sale]:
        return db.execute(select(Sale).offset(skip).limit(limit)).scalars().all()

    @staticmethod
    def get_sale(db: Session, sale_id: int) -> Sale | None:
        return db.get(Sale, sale_id)

    @staticmethod
    def create_sale(db: Session, data: SaleCreate) -> Sale:
        # Calculate totals and reduce inventory
        subtotal = 0.0
        tax_total = 0.0

        sale = Sale(customer_name=data.customer_name)
        db.add(sale)
        db.flush()  # get sale.id

        for item in data.items:
            line_subtotal = item.unit_price * item.quantity
            line_tax = line_subtotal * item.tax_rate
            subtotal += line_subtotal
            tax_total += line_tax

            sale_item = SaleItem(
                sale_id=sale.id,
                drug_id=item.drug_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate,
            )
            db.add(sale_item)

            # Deduct from inventory across batches (FIFO-like simple approach)
            remaining = item.quantity
            inventory_rows = db.execute(
                select(InventoryItem).where(InventoryItem.drug_id == item.drug_id, InventoryItem.quantity_on_hand > 0)
            ).scalars().all()
            for inv in inventory_rows:
                if remaining <= 0:
                    break
                deduct = min(inv.quantity_on_hand, remaining)
                inv.quantity_on_hand -= deduct
                remaining -= deduct

        sale.subtotal = round(subtotal, 2)
        sale.tax_total = round(tax_total, 2)
        sale.total = round(subtotal + tax_total, 2)

        db.commit()
        db.refresh(sale)
        return sale
