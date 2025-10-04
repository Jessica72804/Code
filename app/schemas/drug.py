from pydantic import BaseModel, field_validator
from typing import Optional


class DrugBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    unit_price: float = 0.0
    tax_rate: float = 0.0
    is_active: bool = True


class DrugCreate(DrugBase):
    pass


class DrugUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    unit_price: Optional[float] = None
    tax_rate: Optional[float] = None
    is_active: Optional[bool] = None


class DrugRead(DrugBase):
    id: int

    class Config:
        from_attributes = True
