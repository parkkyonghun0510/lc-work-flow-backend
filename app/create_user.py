import uuid
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models.user import User, UserRole, UserStatus
from .models.branch import Branch
from .models.department import Department
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_default_user():
    db = SessionLocal()
    try:
        # Create tables if they don't exist (handled by create_db.py)
        # User.metadata.create_all(bind=engine)
        # Branch.metadata.create_all(bind=engine)
        # Department.metadata.create_all(bind=engine)

        # Create default branch if it doesn't exist
        default_branch = db.query(Branch).filter(Branch.id == "default_branch").first()
        if not default_branch:
            default_branch = Branch(id="default_branch", name="Default Branch", code="DFLT", address="N/A")
            db.add(default_branch)
            db.commit()
            db.refresh(default_branch)
            print("Default branch created.")

        # Create default department if it doesn't exist
        default_department = db.query(Department).filter(Department.id == "default_department").first()
        if not default_department:
            default_department = Department(id="default_department", name="Default Department", code="DFLT")
            db.add(default_department)
            db.commit()
            db.refresh(default_department)
            print("Default department created.")

        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("Default user 'testuser' already exists.")
            return

        hashed_password = get_password_hash("testpassword")
        db_user = User(
            id=str(uuid.uuid4()),  # Generate a unique ID
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            first_name="Test",  # Added first_name
            last_name="User",   # Added last_name
            role=UserRole.admin,  # Use enum instead of string
            status=UserStatus.active,  # Set status
            department_id="default_department", # Placeholder
            branch_id="default_branch" # Placeholder
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print("Default user 'testuser' created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()