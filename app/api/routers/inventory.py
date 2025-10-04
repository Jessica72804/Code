from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemRead,
    InventoryTransactionCreate,
    InventoryTransactionRead,
)
from app.services import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/items", response_model=list[InventoryItemRead])
def list_items(skip: int = 0, limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    return InventoryService.list_items(db, skip, limit)


@router.post("/items", response_model=InventoryItemRead, status_code=201)
def create_item(payload: InventoryItemCreate, db: Session = Depends(get_db)):
    return InventoryService.create_item(db, payload)


@router.get("/items/{item_id}", response_model=InventoryItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = InventoryService.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}", response_model=InventoryItemRead)
def update_item(item_id: int, payload: InventoryItemUpdate, db: Session = Depends(get_db)):
    item = InventoryService.update_item(db, item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    deleted = InventoryService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return None


@router.post("/transactions", response_model=InventoryTransactionRead, status_code=201)
def add_transaction(payload: InventoryTransactionCreate, db: Session = Depends(get_db)):
    try:
        return InventoryService.add_transaction(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
