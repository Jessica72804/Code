from pydantic import BaseModel
from typing import Optional
from datetime import date


class InventoryItemBase(BaseModel):
    drug_id: int
    supplier_id: Optional[int] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    quantity_on_hand: int = 0
    reorder_level: int = 0
    cost_price: float = 0.0


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    supplier_id: Optional[int] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    quantity_on_hand: Optional[int] = None
    reorder_level: Optional[int] = None
    cost_price: Optional[float] = None


class InventoryItemRead(InventoryItemBase):
    id: int

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    inventory_item_id: int
    transaction_type: str
    quantity_delta: int
    unit_cost: float = 0.0
    note: Optional[str] = None
    transaction_date: Optional[date] = None


class InventoryTransactionRead(BaseModel):
    id: int
    inventory_item_id: int
    transaction_type: str
    quantity_delta: int
    unit_cost: float
    note: Optional[str] = None
    transaction_date: date

    class Config:
        from_attributes = True
