from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class SaleItemIn(BaseModel):
    drug_id: int
    quantity: int
    unit_price: float
    tax_rate: float = 0.0


class SaleCreate(BaseModel):
    sale_date: Optional[date] = None
    customer_name: Optional[str] = None
    items: List[SaleItemIn]


class SaleItemOut(SaleItemIn):
    id: int

    class Config:
        from_attributes = True


class SaleRead(BaseModel):
    id: int
    sale_date: date
    customer_name: Optional[str] = None
    subtotal: float
    tax_total: float
    total: float
    items: List[SaleItemOut]

    class Config:
        from_attributes = True
