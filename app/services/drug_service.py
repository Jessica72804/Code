from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.models import Drug
from app.schemas import DrugCreate, DrugUpdate


class DrugService:
    @staticmethod
    def list_drugs(db: Session, skip: int = 0, limit: int = 50) -> List[Drug]:
        return db.execute(select(Drug).offset(skip).limit(limit)).scalars().all()

    @staticmethod
    def get_drug(db: Session, drug_id: int) -> Optional[Drug]:
        return db.get(Drug, drug_id)

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Optional[Drug]:
        stmt = select(Drug).where(Drug.sku == sku)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def create_drug(db: Session, data: DrugCreate) -> Drug:
        drug = Drug(**data.model_dump())
        db.add(drug)
        db.commit()
        db.refresh(drug)
        return drug

    @staticmethod
    def update_drug(db: Session, drug_id: int, data: DrugUpdate) -> Optional[Drug]:
        drug = db.get(Drug, drug_id)
        if not drug:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(drug, field, value)
        db.commit()
        db.refresh(drug)
        return drug

    @staticmethod
    def delete_drug(db: Session, drug_id: int) -> bool:
        drug = db.get(Drug, drug_id)
        if not drug:
            return False
        db.delete(drug)
        db.commit()
        return True
