#!/usr/bin/env python3

"""
Setup script for LC Work Flow Backend

This script initializes the database and creates default users, branches, and departments.
Run this script after setting up the environment and before starting the application.
"""

import sys
import os

# Add the current directory to the path so that app can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models.branch import Branch
from app.models.department import Department
from app.models import loan  # Import loan models
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_db_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

def create_default_entities():
    db = SessionLocal()
    try:
        # Create default branch if it doesn't exist
        default_branch = db.query(Branch).filter(Branch.id == "default_branch").first()
        if not default_branch:
            default_branch = Branch(id="default_branch", name="Default Branch", code="DFLT", address="N/A")
            db.add(default_branch)
            db.commit()
            db.refresh(default_branch)
            print("Default branch created.")
        else:
            print("Default branch already exists.")

        # Create default department if it doesn't exist
        default_department = db.query(Department).filter(Department.id == "default_department").first()
        if not default_department:
            default_department = Department(id="default_department", name="Default Department", code="DFLT")
            db.add(default_department)
            db.commit()
            db.refresh(default_department)
            print("Default department created.")
        else:
            print("Default department already exists.")

        # Create admin user if it doesn't exist
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_password,
                first_name="Admin",
                last_name="User",
                role=UserRole.admin,
                status=UserStatus.active,
                department_id="default_department",
                branch_id="default_branch"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Admin user 'admin' created successfully.")
        else:
            print("Admin user 'admin' already exists.")

        # Create test user if it doesn't exist
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            hashed_password = get_password_hash("testpassword")
            test_user = User(
                id=str(uuid.uuid4()),
                username="testuser",
                email="test@example.com",
                hashed_password=hashed_password,
                first_name="Test",
                last_name="User",
                role=UserRole.manager,
                status=UserStatus.active,
                department_id="default_department",
                branch_id="default_branch"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("Test user 'testuser' created successfully.")
        else:
            print("Test user 'testuser' already exists.")

        # Create loan officer if it doesn't exist
        loan_officer = db.query(User).filter(User.username == "loanofficer").first()
        if not loan_officer:
            hashed_password = get_password_hash("loan123")
            loan_officer = User(
                id=str(uuid.uuid4()),
                username="loanofficer",
                email="loan@example.com",
                hashed_password=hashed_password,
                first_name="Loan",
                last_name="Officer",
                role=UserRole.loan_officer,
                status=UserStatus.active,
                department_id="default_department",
                branch_id="default_branch"
            )
            db.add(loan_officer)
            db.commit()
            db.refresh(loan_officer)
            print("Loan officer 'loanofficer' created successfully.")
        else:
            print("Loan officer 'loanofficer' already exists.")

    finally:
        db.close()

def main():
    print("===== Setting up LC Work Flow Backend =====\n")
    
    # Create database tables
    create_db_tables()
    print()
    
    # Create default entities
    create_default_entities()
    print()
    
    print("Setup completed successfully!")
    print("\nYou can now start the application with:")
    print("  - Local: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("  - Docker: docker-compose up -d")
    print("  - Podman: ./podman-start.sh")

if __name__ == "__main__":
    main()