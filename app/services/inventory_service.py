from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.models import InventoryItem, InventoryTransaction, Drug, Supplier
from app.schemas import InventoryItemCreate, InventoryItemUpdate, InventoryTransactionCreate


class InventoryService:
    @staticmethod
    def list_items(db: Session, skip: int = 0, limit: int = 50) -> List[InventoryItem]:
        return db.execute(select(InventoryItem).offset(skip).limit(limit)).scalars().all()

    @staticmethod
    def get_item(db: Session, item_id: int) -> Optional[InventoryItem]:
        return db.get(InventoryItem, item_id)

    @staticmethod
    def create_item(db: Session, data: InventoryItemCreate) -> InventoryItem:
        item = InventoryItem(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_item(db: Session, item_id: int, data: InventoryItemUpdate) -> Optional[InventoryItem]:
        item = db.get(InventoryItem, item_id)
        if not item:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        item = db.get(InventoryItem, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    @staticmethod
    def add_transaction(db: Session, data: InventoryTransactionCreate) -> InventoryTransaction:
        tx = InventoryTransaction(**data.model_dump())
        item = db.get(InventoryItem, tx.inventory_item_id)
        if not item:
            raise ValueError("Inventory item not found")
        item.quantity_on_hand += tx.quantity_delta
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def low_stock_items(db: Session) -> List[InventoryItem]:
        stmt = select(InventoryItem).where(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def expiring_soon(db: Session, within_days: int = 30) -> List[InventoryItem]:
        cutoff = date.today().fromordinal(date.today().toordinal() + within_days)
        stmt = select(InventoryItem).where(InventoryItem.expiry_date != None, InventoryItem.expiry_date <= cutoff)  # noqa: E711
        return db.execute(stmt).scalars().all()
