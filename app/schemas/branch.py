from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class BranchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    manager_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_active: bool = True

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    manager_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_active: Optional[bool] = None

class BranchResponse(BranchBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    branches: list[BranchResponse]
    total: int
    skip: int
    limit: int