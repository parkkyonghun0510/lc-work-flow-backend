from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional
from datetime import datetime
import uuid

def get_branch(db: Session, branch_id: str):
    return db.query(models.Branch).filter(models.Branch.id == branch_id).first()

def get_branch_by_code(db: Session, code: str):
    return db.query(models.Branch).filter(models.Branch.code == code).first()

def get_branch_by_name(db: Session, name: str):
    return db.query(models.Branch).filter(models.Branch.name == name).first()

def get_branches(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None):
    query = db.query(models.Branch)
    if is_active is not None:
        query = query.filter(models.Branch.is_active == is_active)
    return query.offset(skip).limit(limit).all()

def create_branch(db: Session, branch: schemas.BranchCreate):
    branch_id = str(uuid.uuid4())
    db_branch = models.Branch(
        id=branch_id,
        name=branch.name,
        code=branch.code,
        address=branch.address,
        phone_number=branch.phone_number,
        email=branch.email,
        manager_id=branch.manager_id,
        latitude=branch.latitude,
        longitude=branch.longitude,
        is_active=branch.is_active if branch.is_active is not None else True
    )
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

def update_branch(db: Session, branch_id: str, branch: schemas.BranchUpdate):
    db_branch = get_branch(db, branch_id)
    if db_branch:
        update_data = branch.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        for key, value in update_data.items():
            setattr(db_branch, key, value)
        db.commit()
        db.refresh(db_branch)
    return db_branch

def delete_branch(db: Session, branch_id: str):
    db_branch = get_branch(db, branch_id)
    if db_branch:
        db.delete(db_branch)
        db.commit()
    return db_branch

def get_active_branches(db: Session):
    return db.query(models.Branch).filter(models.Branch.is_active == True).all()