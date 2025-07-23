from sqlalchemy import Column, String, DateTime, Boolean, Float, Text, ARRAY, Enum, Integer, Date, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum
from ..database import Base

class LoanStatus(enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    disbursed = "disbursed"
    completed = "completed"
    rejected = "rejected"

class IdCardType(enum.Enum):
    nid = "nid"
    passport = "passport"
    driverLicense = "driverLicense"
    cambodianIdentity = "cambodianIdentity"
    none = "none"

class LoanPurposeType(enum.Enum):
    agriculture = "agriculture"
    commerce = "commerce"
    services = "services"
    transportation = "transportation"
    construction = "construction"
    family = "family"
    other = "other"

class ProductType(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    biweekly = "biweekly"
    monthly = "monthly"
    microLoan = "microLoan"

class SyncStatus(enum.Enum):
    synced = "synced"
    pending = "pending"
    failed = "failed"
    created = "created"
    updated = "updated"
    deleted = "deleted"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    server_id = Column(String, nullable=True, index=True)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.pending, nullable=False)

    # Borrower Information
    id_card_type = Column(Enum(IdCardType), nullable=True)
    id_card_images = Column(JSONB, nullable=True) # Changed from id_card_photo_path (String) to support multiple images
    full_name_khmer = Column(String, nullable=True)
    full_name_latin = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    id_number = Column(String, nullable=True)
    portfolio_officer_name = Column(String, nullable=True)

    # Loan/Pawn Details
    requested_amount = Column(Float, nullable=True)
    loan_purposes = Column(ARRAY(Enum(LoanPurposeType)), nullable=True)
    purpose_details = Column(Text, nullable=True)
    product_type = Column(Enum(ProductType), nullable=True)
    desired_loan_term = Column(String, nullable=True)
    requested_disbursement_date = Column(DateTime, nullable=True)
    loan_status = Column(Enum(LoanStatus), default=LoanStatus.draft, nullable=False)
    interest_rate = Column(Float, nullable=True)
    loan_purpose = Column(String, nullable=True) # This seems redundant with loan_purposes, but keeping for now if it's used differently in Flutter

    # New Loan-related fields
    loan_amount = Column(Numeric, nullable=True)
    loan_start_date = Column(Date, nullable=True)
    loan_end_date = Column(Date, nullable=True)

    # Borrower Photos
    borrower_nid_photo_path = Column(String, nullable=True)
    borrower_home_or_land_photo_path = Column(String, nullable=True)
    borrower_business_photo_path = Column(String, nullable=True)

    # Guarantor Photos
    guarantor_name = Column(String, nullable=True)
    guarantor_phone = Column(String, nullable=True)
    guarantor_nid_photo_path = Column(String, nullable=True)
    guarantor_home_or_land_photo_path = Column(String, nullable=True)
    guarantor_business_photo_path = Column(String, nullable=True)
    profile_photo_path = Column(String, nullable=True)

    # Collateral & Documents - Changed to JSONB
    collaterals = Column(JSONB, nullable=True)
    documents = Column(JSONB, nullable=True)
    selected_collateral_types = Column(JSONB, nullable=True) # New field for selected collateral types

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_synced_at = Column(DateTime, nullable=True) # New field for last sync time - no default, should be null initially
    version = Column(Integer, default=1, nullable=False) # New field for optimistic locking