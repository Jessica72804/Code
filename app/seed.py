from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Drug, Supplier


def seed() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(Drug).count() == 0:
            db.add_all(
                [
                    Drug(sku="AMOX500", name="Amoxicillin 500mg", unit_price=0.2, tax_rate=0.05, dosage_form="Capsule"),
                    Drug(sku="PARA500", name="Paracetamol 500mg", unit_price=0.1, tax_rate=0.05, dosage_form="Tablet"),
                ]
            )
        if db.query(Supplier).count() == 0:
            db.add_all(
                [
                    Supplier(name="Health Supplies Ltd", email="contact@healthsupplies.test"),
                    Supplier(name="MediCo", email="sales@medico.test"),
                ]
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
