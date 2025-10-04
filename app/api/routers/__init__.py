from .drug import router as drug_router
from .supplier import router as supplier_router
from .inventory import router as inventory_router
from .sale import router as sale_router
from .report import router as report_router

__all__ = [
    "drug_router",
    "supplier_router",
    "inventory_router",
    "sale_router",
    "report_router",
]
