from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    # Verify department and branch exist
    department = crud.get_department(db, user.department_id)
    if not department:
        raise HTTPException(
            status_code=400,
            detail="Department not found"
        )
    
    branch = crud.get_branch(db, user.branch_id)
    if not branch:
        raise HTTPException(
            status_code=400,
            detail="Branch not found"
        )
    
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by user status"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    db: Session = Depends(get_db)
):
    users = crud.get_users(db, skip=skip, limit=limit, status=status, role=role)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if username is being updated and already exists
    if user.username and user.username != db_user.username:
        existing_user = crud.get_user_by_username(db, username=user.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
    
    # Check if email is being updated and already exists
    if user.email and user.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # Verify department exists if being updated
    if user.department_id:
        department = crud.get_department(db, user.department_id)
        if not department:
            raise HTTPException(
                status_code=400,
                detail="Department not found"
            )
    
    # Verify branch exists if being updated
    if user.branch_id:
        branch = crud.get_branch(db, user.branch_id)
        if not branch:
            raise HTTPException(
                status_code=400,
                detail="Branch not found"
            )
    
    updated_user = crud.update_user(db=db, user_id=user_id, user=user)
    return updated_user

@router.delete("/users/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = crud.delete_user(db=db, user_id=user_id)
    return deleted_user

@router.post("/users/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_password(
    user_id: str, 
    password_data: schemas.PasswordChangeRequest, 
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not crud.verify_password(password_data.current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Update password
    user_update = schemas.UserUpdate(password=password_data.new_password)
    crud.update_user(db=db, user_id=user_id, user=user_update)
    
    return {"message": "Password updated successfully"}