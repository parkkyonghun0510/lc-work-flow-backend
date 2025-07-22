from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserInfo(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: str
    department_id: Optional[str] = Field(None, alias="departmentId")
    branch_id: Optional[str] = Field(None, alias="branchId")

    class Config:
        populate_by_name = True
        from_attributes = True

        @classmethod
        def alias_generator(cls, string: str) -> str:
            return "".join([s.capitalize() if i > 0 else s for i, s in enumerate(string.split("_"))])

class AuthResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field("bearer", alias="tokenType")
    user_info: UserInfo = Field(..., alias="userInfo")
    expires_in: int = Field(..., alias="expiresIn")
    issued_at: datetime = Field(..., alias="issuedAt")

    class Config:
        populate_by_name = True

        @classmethod
        def alias_generator(cls, string: str) -> str:
            return "".join([s.capitalize() if i > 0 else s for i, s in enumerate(string.split("_"))])