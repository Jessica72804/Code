from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.api.routers import drug_router, supplier_router, inventory_router, sale_router, report_router


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(drug_router)
app.include_router(supplier_router)
app.include_router(inventory_router)
app.include_router(sale_router)
app.include_router(report_router)
