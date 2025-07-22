from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from datetime import datetime, timedelta
from ..crud import get_user_by_username, verify_password
from ..auth_utils import create_access_token, create_refresh_token, create_user_token_data, get_token_expiry_time

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/token", response_model=schemas.AuthResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create user info for response
    user_info = schemas.UserInfo(
        id=str(user.id),
        username=str(user.username),
        email=str(user.email),
        role=user.role.value,
        departmentId=str(user.department_id),
        branchId=str(user.branch_id)
    )

    # Create JWT tokens
    access_token_expires = timedelta(minutes=30)
    token_data = create_user_token_data(
        user_id=str(user.id),
        username=str(user.username),
        role=user.role.value
    )

    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    return schemas.AuthResponse(
        accessToken=access_token,
        tokenType="bearer",
        userInfo=user_info,
        expiresIn=int(access_token_expires.total_seconds()),
        issuedAt=datetime.utcnow()
    )