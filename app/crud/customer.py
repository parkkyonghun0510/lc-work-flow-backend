from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime
from sqlalchemy.sql import func

def get_customer(db: Session, customer_id: str):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    # Convert to dict without excluding unset fields to preserve None values
    customer_data = customer.model_dump(by_alias=False, exclude_unset=False)
    db_customer = models.Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: str, customer: schemas.CustomerUpdate):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True, by_alias=False)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db_customer.last_synced_at = datetime.utcnow() # type: ignore # Explicitly update last_synced_at
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: str):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer