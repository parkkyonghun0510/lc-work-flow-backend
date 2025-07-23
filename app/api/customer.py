from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from typing import List
from datetime import datetime

router = APIRouter()

# Helper function to convert Pydantic model to dictionary with datetime serialization
def customer_to_dict(customer_obj: schemas.CustomerResponse):
    data = customer_obj.dict(by_alias=True)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer.id)
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer with this ID already exists")
    created_customer = crud.create_customer(db=db, customer=customer)
    return schemas.CustomerResponse.model_validate(created_customer)

@router.get("/customers/", response_model=List[schemas.CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return [schemas.CustomerResponse.model_validate(customer) for customer in customers]

@router.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def read_customer(customer_id: str, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return schemas.CustomerResponse.model_validate(db_customer)

@router.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: str, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.refresh(db_customer) # Force refresh to ensure all attributes are loaded

    # Optimistic locking check
    current_version = db_customer.version
    if current_version != customer.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "errorMessage": "Conflict: Customer record has been updated by another process.",
                "conflictData": customer_to_dict(schemas.CustomerResponse.model_validate(db_customer))
            }
        )
    
    # Increment version for successful update
    customer.version += 1
    
    updated_customer = crud.update_customer(db=db, customer_id=customer_id, customer=customer)
    return schemas.CustomerResponse.model_validate(updated_customer)

@router.delete("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    # Convert to response before deletion
    response_data = schemas.CustomerResponse.model_validate(db_customer)
    crud.delete_customer(db=db, customer_id=customer_id)
    return response_data