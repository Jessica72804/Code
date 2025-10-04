from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import DrugCreate, DrugUpdate, DrugRead
from app.services import DrugService

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("/", response_model=list[DrugRead])
def list_drugs(skip: int = 0, limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    return DrugService.list_drugs(db, skip, limit)


@router.post("/", response_model=DrugRead, status_code=201)
def create_drug(payload: DrugCreate, db: Session = Depends(get_db)):
    existing = DrugService.get_by_sku(db, payload.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    return DrugService.create_drug(db, payload)


@router.get("/{drug_id}", response_model=DrugRead)
def get_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = DrugService.get_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug


@router.put("/{drug_id}", response_model=DrugRead)
def update_drug(drug_id: int, payload: DrugUpdate, db: Session = Depends(get_db)):
    drug = DrugService.update_drug(db, drug_id, payload)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug


@router.delete("/{drug_id}", status_code=204)
def delete_drug(drug_id: int, db: Session = Depends(get_db)):
    deleted = DrugService.delete_drug(db, drug_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Drug not found")
    return None
