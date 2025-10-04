from __future__ import annotations
from sqlalchemy import String, Integer, Date, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Drug(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(String(128), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan"
    )

    sale_items: Mapped[list["SaleItem"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan"
    )
