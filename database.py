from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    merchant = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, default="Uncategorized")
    is_anomaly = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def insert_transactions(records: list[dict]):
    db = SessionLocal()
    try:
        for r in records:
            obj = Transaction(
                date=r["date"],
                merchant=r["merchant"],
                amount=r["amount"],
                category=r.get("category", "Uncategorized"),
                is_anomaly=r.get("is_anomaly", False),
            )
            db.add(obj)
        db.commit()
    finally:
        db.close()


def fetch_all_transactions() -> list[dict]:
    db = SessionLocal()
    try:
        rows = db.query(Transaction).order_by(Transaction.date).all()
        return [
            {
                "id": r.id,
                "date": r.date,
                "merchant": r.merchant,
                "amount": r.amount,
                "category": r.category,
                "is_anomaly": r.is_anomaly,
            }
            for r in rows
        ]
    finally:
        db.close()


def clear_transactions():
    db = SessionLocal()
    try:
        db.query(Transaction).delete()
        db.commit()
    finally:
        db.close()
