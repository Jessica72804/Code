from __future__ import annotations
from sqlalchemy import String, Integer, ForeignKey, Date, Float, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from enum import Enum as PyEnum

from app.db.base import Base


class InventoryTransactionType(str, PyEnum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    drug_id: Mapped[int] = mapped_column(ForeignKey("drugs.id"), index=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)

    batch_number: Mapped[str | None] = mapped_column(String(128))
    expiry_date: Mapped[date | None] = mapped_column(Date)

    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    cost_price: Mapped[float] = mapped_column(Float, default=0.0)

    drug: Mapped["Drug"] = relationship(back_populates="inventory_items")
    supplier: Mapped["Supplier"] = relationship(back_populates="inventory_items")

    transactions: Mapped[list["InventoryTransaction"]] = relationship(
        back_populates="inventory_item", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_inventory_unique_batch", "drug_id", "batch_number", unique=False),
    )


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(32))
    quantity_delta: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    note: Mapped[str | None] = mapped_column(String(255))
    transaction_date: Mapped[date] = mapped_column(Date, default=date.today)

    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="transactions")
