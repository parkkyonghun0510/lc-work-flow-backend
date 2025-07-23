from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Optional, Any
from enum import Enum
from decimal import Decimal # Import Decimal
import json

class IdCardType(str, Enum):
    nid = "nid"
    passport = "passport"
    driverLicense = "driverLicense"
    cambodianIdentity = "cambodianIdentity"
    none = "none"

class LoanPurposeType(str, Enum):
    agriculture = "agriculture"
    commerce = "commerce"
    services = "services"
    transportation = "transportation"
    construction = "construction"
    family = "family"
    other = "other"

class ProductType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    biweekly = "biweekly"
    monthly = "monthly"
    microLoan = "microLoan"

class LoanStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    disbursed = "disbursed"
    completed = "completed"
    rejected = "rejected"

class SyncStatus(str, Enum):
    synced = "synced"
    pending = "pending"
    failed = "failed"
    created = "created"
    updated = "updated"
    deleted = "deleted"

class CustomerBase(BaseModel):
    server_id: Optional[str] = Field(None, alias="serverId")
    sync_status: SyncStatus = Field(default=SyncStatus.pending, alias="syncStatus")
    id_card_type: Optional[IdCardType] = Field(None, alias="idCardType")
    id_card_images: Optional[List[Any]] = Field(default_factory=list, alias="idCardImages")
    full_name_khmer: Optional[str] = Field(None, alias="fullNameKhmer")
    full_name_latin: Optional[str] = Field(None, alias="fullNameLatin")
    date_of_birth: Optional[datetime] = Field(None, alias="dateOfBirth")
    id_number: Optional[str] = Field(None, alias="idNumber")
    portfolio_officer_name: Optional[str] = Field(None, alias="portfolioOfficerName")
    requested_amount: Optional[float] = Field(None, alias="requestedAmount")
    loan_purposes: Optional[List[LoanPurposeType]] = Field(None, alias="loanPurposes")
    purpose_details: Optional[str] = Field(None, alias="purposeDetails")
    product_type: Optional[ProductType] = Field(None, alias="productType")
    desired_loan_term: Optional[str] = Field(None, alias="desiredLoanTerm")
    requested_disbursement_date: Optional[datetime] = Field(None, alias="requestedDisbursementDate")
    loan_status: LoanStatus = Field(default=LoanStatus.draft, alias="loanStatus")
    interest_rate: Optional[float] = Field(None, alias="interestRate")
    loan_purpose: Optional[str] = Field(None, alias="loanPurpose")
    loan_amount: Optional[float] = Field(None, alias="loanAmount")
    loan_start_date: Optional[date] = Field(None, alias="loanStartDate")
    loan_end_date: Optional[date] = Field(None, alias="loanEndDate")
    borrower_nid_photo_path: Optional[str] = Field(None, alias="borrowerNidPhotoPath")
    borrower_home_or_land_photo_path: Optional[str] = Field(None, alias="borrowerHomeOrLandPhotoPath")
    borrower_business_photo_path: Optional[str] = Field(None, alias="borrowerBusinessPhotoPath")
    guarantor_name: Optional[str] = Field(None, alias="guarantorName")
    guarantor_phone: Optional[str] = Field(None, alias="guarantorPhone")
    guarantor_nid_photo_path: Optional[str] = Field(None, alias="guarantorNidPhotoPath")
    guarantor_home_or_land_photo_path: Optional[str] = Field(None, alias="guarantorHomeOrLandPhotoPath")
    guarantor_business_photo_path: Optional[str] = Field(None, alias="guarantorBusinessPhotoPath")
    profile_photo_path: Optional[str] = Field(None, alias="profilePhotoPath")
    collaterals: Optional[List[Any]] = Field(default_factory=list)
    documents: Optional[List[Any]] = Field(default_factory=list)
    selected_collateral_types: Optional[List[Any]] = Field(default_factory=list, alias="selectedCollateralTypes")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    last_synced_at: Optional[datetime] = Field(None, alias="lastSyncedAt")
    version: int = Field(default=1)

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    }



    @field_validator('id_card_images', 'selected_collateral_types', 'collaterals', 'documents', mode='before')
    @classmethod
    def validate_jsonb_list_fields(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            # If it's a string that looks like a JSON list, try to parse it
            if isinstance(v, str) and v.strip().startswith('[') and v.strip().endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass # Let Pydantic handle the validation error later
            return [v] # If not a list, wrap it in a list. This might be too permissive, but for now...
        return v

    @field_validator('loan_amount', mode='before')
    @classmethod
    def validate_loan_amount(cls, v):
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v

    @field_validator('loan_start_date', 'loan_end_date', 'last_synced_at', mode='before')
    @classmethod
    def validate_date_fields(cls, v):
        if v is None:
            return None
        # If it's a string, try to parse it. FastAPI/Pydantic usually handles ISO format automatically.
        if isinstance(v, str):
            try:
                if 'T' in v: # Assume datetime
                    return datetime.fromisoformat(v)
                else: # Assume date
                    return date.fromisoformat(v)
            except ValueError:
                pass # Let Pydantic handle the validation error later
        return v


class CustomerCreate(CustomerBase):
    id: str

class CustomerUpdate(CustomerBase):
    version: int = Field(..., description="Version for optimistic locking")

class CustomerInDB(CustomerBase):
    id: str

class CustomerResponse(CustomerBase):
    id: str

class ErrorResponse(BaseModel):
    errorMessage: str = Field(..., alias="errorMessage")
    conflictData: Optional[CustomerResponse] = Field(None, alias="conflictData")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}