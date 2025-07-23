from sqlalchemy import Column, String, DateTime, Boolean, Enum, Float, Text, Integer
from datetime import datetime
import enum
from ..database import Base

class LoanStatus(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    disbursed = "disbursed"
    closed = "closed"
    defaulted = "defaulted"

class LoanType(enum.Enum):
    personal = "personal"
    home = "home"
    auto = "auto"
    business = "business"
    education = "education"
    agriculture = "agriculture"

class CollateralType(enum.Enum):
    property = "property"
    vehicle = "vehicle"
    gold = "gold"
    fixed_deposit = "fixed_deposit"
    shares = "shares"
    none = "none"

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String, primary_key=True, index=True)
    application_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, nullable=False)  # Foreign key to customers
    loan_type = Column(Enum(LoanType), nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=True)  # To be set during approval
    monthly_income = Column(Float, nullable=False)
    employment_type = Column(String, nullable=False)  # employed, self_employed, business, retired
    employer_name = Column(String, nullable=True)
    work_experience_years = Column(Integer, nullable=True)
    
    # Collateral information
    collateral_type = Column(Enum(CollateralType), default=CollateralType.none)
    collateral_value = Column(Float, nullable=True)
    collateral_description = Column(Text, nullable=True)
    
    # Application status and workflow
    status = Column(Enum(LoanStatus), default=LoanStatus.draft, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    disbursed_at = Column(DateTime, nullable=True)
    
    # Staff assignments
    assigned_officer_id = Column(String, nullable=True)  # Foreign key to users
    reviewed_by_id = Column(String, nullable=True)  # Foreign key to users
    approved_by_id = Column(String, nullable=True)  # Foreign key to users
    
    # Comments and notes
    officer_notes = Column(Text, nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Document tracking
    documents_submitted = Column(Boolean, default=False)
    documents_verified = Column(Boolean, default=False)
    credit_check_completed = Column(Boolean, default=False)
    
    # Calculated fields
    debt_to_income_ratio = Column(Float, nullable=True)
    credit_score = Column(Integer, nullable=True)
    risk_category = Column(String, nullable=True)  # low, medium, high
    
    # Branch and department
    branch_id = Column(String, nullable=False)
    department_id = Column(String, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)  # For optimistic locking

class LoanDocument(Base):
    __tablename__ = "loan_documents"

    id = Column(String, primary_key=True, index=True)
    loan_application_id = Column(String, nullable=False)  # Foreign key to loan_applications
    document_type = Column(String, nullable=False)  # id_proof, income_proof, address_proof, etc.
    document_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    uploaded_by_id = Column(String, nullable=False)  # Foreign key to users
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(String, nullable=True)  # Foreign key to users
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)