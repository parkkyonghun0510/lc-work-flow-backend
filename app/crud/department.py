from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional
from datetime import datetime
import uuid

def get_department(db: Session, department_id: str):
    return db.query(models.Department).filter(models.Department.id == department_id).first()

def get_department_by_code(db: Session, code: str):
    return db.query(models.Department).filter(models.Department.code == code).first()

def get_department_by_name(db: Session, name: str):
    return db.query(models.Department).filter(models.Department.name == name).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None):
    query = db.query(models.Department)
    if is_active is not None:
        query = query.filter(models.Department.is_active == is_active)
    return query.offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    department_id = str(uuid.uuid4())
    db_department = models.Department(
        id=department_id,
        name=department.name,
        code=department.code,
        description=department.description,
        manager_id=department.manager_id,
        is_active=department.is_active if department.is_active is not None else True
    )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id: str, department: schemas.DepartmentUpdate):
    db_department = get_department(db, department_id)
    if db_department:
        update_data = department.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        for key, value in update_data.items():
            setattr(db_department, key, value)
        db.commit()
        db.refresh(db_department)
    return db_department

def delete_department(db: Session, department_id: str):
    db_department = get_department(db, department_id)
    if db_department:
        db.delete(db_department)
        db.commit()
    return db_department

def get_active_departments(db: Session):
    return db.query(models.Department).filter(models.Department.is_active == True).all()