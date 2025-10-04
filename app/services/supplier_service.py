from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.models import Supplier
from app.schemas import SupplierCreate, SupplierUpdate


class SupplierService:
    @staticmethod
    def list_suppliers(db: Session, skip: int = 0, limit: int = 50) -> List[Supplier]:
        return db.execute(select(Supplier).offset(skip).limit(limit)).scalars().all()

    @staticmethod
    def get_supplier(db: Session, supplier_id: int) -> Optional[Supplier]:
        return db.get(Supplier, supplier_id)

    @staticmethod
    def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
        supplier = Supplier(**data.model_dump())
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def update_supplier(db: Session, supplier_id: int, data: SupplierUpdate) -> Optional[Supplier]:
        supplier = db.get(Supplier, supplier_id)
        if not supplier:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(supplier, field, value)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete_supplier(db: Session, supplier_id: int) -> bool:
        supplier = db.get(Supplier, supplier_id)
        if not supplier:
            return False
        db.delete(supplier)
        db.commit()
        return True
