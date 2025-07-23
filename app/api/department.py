from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from typing import List, Optional

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/departments/", response_model=schemas.DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    # Check if department name already exists
    db_department = crud.get_department_by_name(db, name=department.name)
    if db_department:
        raise HTTPException(
            status_code=400,
            detail="Department name already exists"
        )
    
    # Check if department code already exists
    db_department = crud.get_department_by_code(db, code=department.code)
    if db_department:
        raise HTTPException(
            status_code=400,
            detail="Department code already exists"
        )
    
    # Verify manager exists if provided
    if department.manager_id:
        manager = crud.get_user(db, department.manager_id)
        if not manager:
            raise HTTPException(
                status_code=400,
                detail="Manager not found"
            )
        # Check if manager has appropriate role
        if manager.role not in [models.UserRole.admin, models.UserRole.manager]:
            raise HTTPException(
                status_code=400,
                detail="User does not have manager privileges"
            )
    
    return crud.create_department(db=db, department=department)

@router.get("/departments/", response_model=List[schemas.DepartmentResponse])
def read_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    departments = crud.get_departments(db, skip=skip, limit=limit, is_active=is_active)
    return departments

@router.get("/departments/active", response_model=List[schemas.DepartmentResponse])
def read_active_departments(db: Session = Depends(get_db)):
    """Get all active departments for dropdown/selection purposes"""
    departments = crud.get_active_departments(db)
    return departments

@router.get("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def read_department(department_id: str, db: Session = Depends(get_db)):
    db_department = crud.get_department(db, department_id=department_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department

@router.put("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def update_department(department_id: str, department: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    db_department = crud.get_department(db, department_id=department_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if department name is being updated and already exists
    if department.name and department.name != db_department.name:
        existing_department = crud.get_department_by_name(db, name=department.name)
        if existing_department:
            raise HTTPException(
                status_code=400,
                detail="Department name already exists"
            )
    
    # Check if department code is being updated and already exists
    if department.code and department.code != db_department.code:
        existing_department = crud.get_department_by_code(db, code=department.code)
        if existing_department:
            raise HTTPException(
                status_code=400,
                detail="Department code already exists"
            )
    
    # Verify manager exists if being updated
    if department.manager_id:
        manager = crud.get_user(db, department.manager_id)
        if not manager:
            raise HTTPException(
                status_code=400,
                detail="Manager not found"
            )
        # Check if manager has appropriate role
        if manager.role not in [models.UserRole.admin, models.UserRole.manager]:
            raise HTTPException(
                status_code=400,
                detail="User does not have manager privileges"
            )
    
    updated_department = crud.update_department(db=db, department_id=department_id, department=department)
    return updated_department

@router.delete("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def delete_department(department_id: str, db: Session = Depends(get_db)):
    db_department = crud.get_department(db, department_id=department_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if department has associated users
    users_in_department = crud.get_users(db, skip=0, limit=1)
    department_users = [user for user in users_in_department if user.department_id == department_id]
    if department_users:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete department with associated users. Please reassign users first."
        )
    
    deleted_department = crud.delete_department(db=db, department_id=department_id)
    return deleted_department