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

@router.post("/branches/", response_model=schemas.BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(branch: schemas.BranchCreate, db: Session = Depends(get_db)):
    # Check if branch name already exists
    db_branch = crud.get_branch_by_name(db, name=branch.name)
    if db_branch:
        raise HTTPException(
            status_code=400,
            detail="Branch name already exists"
        )
    
    # Check if branch code already exists
    db_branch = crud.get_branch_by_code(db, code=branch.code)
    if db_branch:
        raise HTTPException(
            status_code=400,
            detail="Branch code already exists"
        )
    
    # Verify manager exists if provided
    if branch.manager_id:
        manager = crud.get_user(db, branch.manager_id)
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
    
    return crud.create_branch(db=db, branch=branch)

@router.get("/branches/", response_model=List[schemas.BranchResponse])
def read_branches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    branches = crud.get_branches(db, skip=skip, limit=limit, is_active=is_active)
    return branches

@router.get("/branches/active", response_model=List[schemas.BranchResponse])
def read_active_branches(db: Session = Depends(get_db)):
    """Get all active branches for dropdown/selection purposes"""
    branches = crud.get_active_branches(db)
    return branches

@router.get("/branches/{branch_id}", response_model=schemas.BranchResponse)
def read_branch(branch_id: str, db: Session = Depends(get_db)):
    db_branch = crud.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch

@router.put("/branches/{branch_id}", response_model=schemas.BranchResponse)
def update_branch(branch_id: str, branch: schemas.BranchUpdate, db: Session = Depends(get_db)):
    db_branch = crud.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if branch name is being updated and already exists
    if branch.name and branch.name != db_branch.name:
        existing_branch = crud.get_branch_by_name(db, name=branch.name)
        if existing_branch:
            raise HTTPException(
                status_code=400,
                detail="Branch name already exists"
            )
    
    # Check if branch code is being updated and already exists
    if branch.code and branch.code != db_branch.code:
        existing_branch = crud.get_branch_by_code(db, code=branch.code)
        if existing_branch:
            raise HTTPException(
                status_code=400,
                detail="Branch code already exists"
            )
    
    # Verify manager exists if being updated
    if branch.manager_id:
        manager = crud.get_user(db, branch.manager_id)
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
    
    updated_branch = crud.update_branch(db=db, branch_id=branch_id, branch=branch)
    return updated_branch

@router.delete("/branches/{branch_id}", response_model=schemas.BranchResponse)
def delete_branch(branch_id: str, db: Session = Depends(get_db)):
    db_branch = crud.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if branch has associated users
    users_in_branch = crud.get_users(db, skip=0, limit=1)
    branch_users = [user for user in users_in_branch if user.branch_id == branch_id]
    if branch_users:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete branch with associated users. Please reassign users first."
        )
    
    deleted_branch = crud.delete_branch(db=db, branch_id=branch_id)
    return deleted_branch