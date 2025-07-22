from sqlalchemy import Column, String, DateTime, Boolean, Enum
from datetime import datetime
import enum
from ..database import Base

class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    officer = "officer"
    viewer = "viewer"

class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.officer, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    department_id = Column(String, nullable=False)
    branch_id = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)