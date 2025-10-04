from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import SaleCreate, SaleRead
from app.services import SaleService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=list[SaleRead])
def list_sales(skip: int = 0, limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    return SaleService.list_sales(db, skip, limit)


@router.post("/", response_model=SaleRead, status_code=201)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    return SaleService.create_sale(db, payload)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = SaleService.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale
