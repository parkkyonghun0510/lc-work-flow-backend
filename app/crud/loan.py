from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional
from datetime import datetime
import uuid
import math

def generate_application_number() -> str:
    """Generate a unique application number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"LA{timestamp}{random_suffix}"

def get_loan_application(db: Session, application_id: str):
    return db.query(models.LoanApplication).filter(models.LoanApplication.id == application_id).first()

def get_loan_application_by_number(db: Session, application_number: str):
    return db.query(models.LoanApplication).filter(models.LoanApplication.application_number == application_number).first()

def get_loan_applications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    loan_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    assigned_officer_id: Optional[str] = None,
    branch_id: Optional[str] = None
):
    query = db.query(models.LoanApplication)
    
    if status:
        query = query.filter(models.LoanApplication.status == status)
    if loan_type:
        query = query.filter(models.LoanApplication.loan_type == loan_type)
    if customer_id:
        query = query.filter(models.LoanApplication.customer_id == customer_id)
    if assigned_officer_id:
        query = query.filter(models.LoanApplication.assigned_officer_id == assigned_officer_id)
    if branch_id:
        query = query.filter(models.LoanApplication.branch_id == branch_id)
    
    return query.order_by(models.LoanApplication.created_at.desc()).offset(skip).limit(limit).all()

def create_loan_application(db: Session, application: schemas.LoanApplicationCreate, created_by_id: str):
    application_id = str(uuid.uuid4())
    application_number = generate_application_number()
    
    # Calculate debt-to-income ratio
    debt_to_income_ratio = (application.loan_amount / application.loan_tenure_months) / application.monthly_income * 100
    
    db_application = models.LoanApplication(
        id=application_id,
        application_number=application_number,
        customer_id=application.customer_id,
        loan_type=application.loan_type,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        loan_tenure_months=application.loan_tenure_months,
        monthly_income=application.monthly_income,
        employment_type=application.employment_type,
        employer_name=application.employer_name,
        work_experience_years=application.work_experience_years,
        collateral_type=application.collateral_type,
        collateral_value=application.collateral_value,
        collateral_description=application.collateral_description,
        branch_id=application.branch_id,
        department_id=application.department_id,
        debt_to_income_ratio=debt_to_income_ratio,
        assigned_officer_id=created_by_id  # Auto-assign to creator initially
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_loan_application(db: Session, application_id: str, application: schemas.LoanApplicationUpdate):
    db_application = get_loan_application(db, application_id)
    if db_application:
        update_data = application.dict(exclude_unset=True, exclude={'version'})
        
        # Recalculate debt-to-income ratio if relevant fields changed
        if 'loan_amount' in update_data or 'loan_tenure_months' in update_data or 'monthly_income' in update_data:
            loan_amount = update_data.get('loan_amount', db_application.loan_amount)
            loan_tenure = update_data.get('loan_tenure_months', db_application.loan_tenure_months)
            monthly_income = update_data.get('monthly_income', db_application.monthly_income)
            update_data['debt_to_income_ratio'] = (loan_amount / loan_tenure) / monthly_income * 100
        
        update_data['updated_at'] = datetime.utcnow()
        update_data['version'] = db_application.version + 1
        
        for key, value in update_data.items():
            setattr(db_application, key, value)
        
        db.commit()
        db.refresh(db_application)
    return db_application

def update_loan_application_status(
    db: Session, 
    application_id: str, 
    status_update: schemas.LoanApplicationStatusUpdate,
    updated_by_id: str
):
    db_application = get_loan_application(db, application_id)
    if db_application:
        # Update status and related fields
        db_application.status = status_update.status
        db_application.updated_at = datetime.utcnow()
        db_application.version = db_application.version + 1
        
        current_time = datetime.utcnow()
        
        if status_update.status == models.LoanStatus.submitted:
            db_application.submitted_at = current_time
        elif status_update.status == models.LoanStatus.under_review:
            db_application.reviewed_at = current_time
            db_application.reviewed_by_id = updated_by_id
            if status_update.comments:
                db_application.reviewer_comments = status_update.comments
        elif status_update.status == models.LoanStatus.approved:
            db_application.approved_at = current_time
            db_application.approved_by_id = updated_by_id
            if status_update.interest_rate:
                db_application.interest_rate = status_update.interest_rate
            if status_update.comments:
                db_application.reviewer_comments = status_update.comments
        elif status_update.status == models.LoanStatus.rejected:
            db_application.rejected_at = current_time
            db_application.reviewed_by_id = updated_by_id
            if status_update.rejection_reason:
                db_application.rejection_reason = status_update.rejection_reason
            if status_update.comments:
                db_application.reviewer_comments = status_update.comments
        elif status_update.status == models.LoanStatus.disbursed:
            db_application.disbursed_at = current_time
        
        db.commit()
        db.refresh(db_application)
    return db_application

def delete_loan_application(db: Session, application_id: str):
    db_application = get_loan_application(db, application_id)
    if db_application:
        db.delete(db_application)
        db.commit()
    return db_application

def assign_loan_officer(db: Session, application_id: str, officer_id: str):
    db_application = get_loan_application(db, application_id)
    if db_application:
        db_application.assigned_officer_id = officer_id
        db_application.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_application)
    return db_application

# Loan Document CRUD operations
def get_loan_document(db: Session, document_id: str):
    return db.query(models.LoanDocument).filter(models.LoanDocument.id == document_id).first()

def get_loan_documents(db: Session, application_id: str):
    return db.query(models.LoanDocument).filter(
        models.LoanDocument.loan_application_id == application_id
    ).order_by(models.LoanDocument.created_at.desc()).all()

def create_loan_document(db: Session, document: schemas.LoanDocumentCreate):
    document_id = str(uuid.uuid4())
    db_document = models.LoanDocument(
        id=document_id,
        loan_application_id=document.loan_application_id,
        document_type=document.document_type,
        document_name=document.document_name,
        file_path=document.file_path,
        file_size=document.file_size,
        mime_type=document.mime_type,
        uploaded_by_id=document.uploaded_by_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_loan_document(db: Session, document_id: str, document: schemas.LoanDocumentUpdate, verified_by_id: str = None):
    db_document = get_loan_document(db, document_id)
    if db_document:
        update_data = document.dict(exclude_unset=True)
        
        if document.is_verified is not None:
            update_data['verified_by_id'] = verified_by_id
            update_data['verified_at'] = datetime.utcnow()
        
        update_data['updated_at'] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(db_document, key, value)
        
        db.commit()
        db.refresh(db_document)
    return db_document

def delete_loan_document(db: Session, document_id: str):
    db_document = get_loan_document(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
    return db_document

# Loan calculation utilities
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate Equated Monthly Installment (EMI)"""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / tenure_months
    
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)

def generate_emi_schedule(principal: float, annual_rate: float, tenure_months: int) -> List[dict]:
    """Generate EMI schedule with principal and interest breakdown"""
    monthly_rate = annual_rate / (12 * 100)
    emi = calculate_emi(principal, annual_rate, tenure_months)
    
    schedule = []
    outstanding_principal = principal
    
    for month in range(1, tenure_months + 1):
        interest_component = outstanding_principal * monthly_rate
        principal_component = emi - interest_component
        outstanding_principal -= principal_component
        
        schedule.append({
            "month": month,
            "emi": round(emi, 2),
            "principal": round(principal_component, 2),
            "interest": round(interest_component, 2),
            "outstanding_principal": round(max(0, outstanding_principal), 2)
        })
    
    return schedule

def get_loan_summary_stats(db: Session, branch_id: Optional[str] = None) -> dict:
    """Get summary statistics for loan applications"""
    query = db.query(models.LoanApplication)
    if branch_id:
        query = query.filter(models.LoanApplication.branch_id == branch_id)
    
    applications = query.all()
    
    total_applications = len(applications)
    if total_applications == 0:
        return {
            "total_applications": 0,
            "pending_review": 0,
            "approved_applications": 0,
            "rejected_applications": 0,
            "disbursed_loans": 0,
            "total_loan_amount": 0,
            "average_loan_amount": 0,
            "by_status": {},
            "by_loan_type": {},
            "by_risk_category": {}
        }
    
    # Count by status
    by_status = {}
    by_loan_type = {}
    by_risk_category = {}
    
    total_amount = sum(app.loan_amount for app in applications)
    
    for app in applications:
        # Status counts
        status = app.status.value
        by_status[status] = by_status.get(status, 0) + 1
        
        # Loan type counts
        loan_type = app.loan_type.value
        by_loan_type[loan_type] = by_loan_type.get(loan_type, 0) + 1
        
        # Risk category counts
        if app.risk_category:
            risk_cat = app.risk_category
            by_risk_category[risk_cat] = by_risk_category.get(risk_cat, 0) + 1
    
    return {
        "total_applications": total_applications,
        "pending_review": by_status.get("under_review", 0),
        "approved_applications": by_status.get("approved", 0),
        "rejected_applications": by_status.get("rejected", 0),
        "disbursed_loans": by_status.get("disbursed", 0),
        "total_loan_amount": round(total_amount, 2),
        "average_loan_amount": round(total_amount / total_applications, 2),
        "by_status": by_status,
        "by_loan_type": by_loan_type,
        "by_risk_category": by_risk_category
    }