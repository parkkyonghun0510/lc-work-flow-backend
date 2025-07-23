from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LoanStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    disbursed = "disbursed"
    closed = "closed"
    defaulted = "defaulted"

class LoanType(str, Enum):
    personal = "personal"
    home = "home"
    auto = "auto"
    business = "business"
    education = "education"
    agriculture = "agriculture"

class CollateralType(str, Enum):
    property = "property"
    vehicle = "vehicle"
    gold = "gold"
    fixed_deposit = "fixed_deposit"
    shares = "shares"
    none = "none"

class EmploymentType(str, Enum):
    employed = "employed"
    self_employed = "self_employed"
    business = "business"
    retired = "retired"

class RiskCategory(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class LoanApplicationBase(BaseModel):
    customer_id: str
    loan_type: LoanType
    loan_amount: float = Field(..., gt=0, description="Loan amount must be positive")
    loan_purpose: str = Field(..., min_length=10, max_length=500)
    loan_tenure_months: int = Field(..., ge=6, le=360, description="Loan tenure between 6 and 360 months")
    monthly_income: float = Field(..., gt=0, description="Monthly income must be positive")
    employment_type: EmploymentType
    employer_name: Optional[str] = Field(None, max_length=200)
    work_experience_years: Optional[int] = Field(None, ge=0, le=50)
    collateral_type: CollateralType = CollateralType.none
    collateral_value: Optional[float] = Field(None, ge=0)
    collateral_description: Optional[str] = Field(None, max_length=1000)
    branch_id: str
    department_id: str

    @validator('collateral_value')
    def validate_collateral_value(cls, v, values):
        if values.get('collateral_type') != CollateralType.none and v is None:
            raise ValueError('Collateral value is required when collateral type is specified')
        return v

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationUpdate(BaseModel):
    loan_type: Optional[LoanType] = None
    loan_amount: Optional[float] = Field(None, gt=0)
    loan_purpose: Optional[str] = Field(None, min_length=10, max_length=500)
    loan_tenure_months: Optional[int] = Field(None, ge=6, le=360)
    monthly_income: Optional[float] = Field(None, gt=0)
    employment_type: Optional[EmploymentType] = None
    employer_name: Optional[str] = Field(None, max_length=200)
    work_experience_years: Optional[int] = Field(None, ge=0, le=50)
    collateral_type: Optional[CollateralType] = None
    collateral_value: Optional[float] = Field(None, ge=0)
    collateral_description: Optional[str] = Field(None, max_length=1000)
    officer_notes: Optional[str] = Field(None, max_length=2000)
    version: int  # For optimistic locking

class LoanApplicationStatusUpdate(BaseModel):
    status: LoanStatus
    comments: Optional[str] = Field(None, max_length=2000)
    interest_rate: Optional[float] = Field(None, ge=0, le=50)
    rejection_reason: Optional[str] = Field(None, max_length=1000)
    version: int  # For optimistic locking

class LoanApplicationResponse(LoanApplicationBase):
    id: str
    application_number: str
    status: LoanStatus
    interest_rate: Optional[float] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    disbursed_at: Optional[datetime] = None
    assigned_officer_id: Optional[str] = None
    reviewed_by_id: Optional[str] = None
    approved_by_id: Optional[str] = None
    officer_notes: Optional[str] = None
    reviewer_comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    documents_submitted: bool = False
    documents_verified: bool = False
    credit_check_completed: bool = False
    debt_to_income_ratio: Optional[float] = None
    credit_score: Optional[int] = None
    risk_category: Optional[RiskCategory] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True

class LoanApplicationListResponse(BaseModel):
    applications: List[LoanApplicationResponse]
    total: int
    skip: int
    limit: int

class LoanDocumentBase(BaseModel):
    loan_application_id: str
    document_type: str = Field(..., min_length=1, max_length=100)
    document_name: str = Field(..., min_length=1, max_length=200)
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class LoanDocumentCreate(LoanDocumentBase):
    uploaded_by_id: str

class LoanDocumentUpdate(BaseModel):
    document_name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_verified: Optional[bool] = None
    verification_notes: Optional[str] = Field(None, max_length=1000)

class LoanDocumentResponse(LoanDocumentBase):
    id: str
    uploaded_by_id: str
    is_verified: bool = False
    verified_by_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoanSummaryStats(BaseModel):
    total_applications: int
    pending_review: int
    approved_applications: int
    rejected_applications: int
    disbursed_loans: int
    total_loan_amount: float
    average_loan_amount: float
    by_status: dict
    by_loan_type: dict
    by_risk_category: dict

class LoanCalculationRequest(BaseModel):
    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0, le=50)
    loan_tenure_months: int = Field(..., ge=6, le=360)

class LoanCalculationResponse(BaseModel):
    loan_amount: float
    interest_rate: float
    loan_tenure_months: int
    monthly_emi: float
    total_interest: float
    total_amount: float
    emi_schedule: List[dict]  # Monthly EMI breakdown