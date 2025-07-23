from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal
from typing import List, Optional
from datetime import datetime
import os
from pathlib import Path

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/loan-applications/", response_model=schemas.LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_loan_application(
    application: schemas.LoanApplicationCreate, 
    created_by_id: str = Query(..., description="ID of the user creating the application"),
    db: Session = Depends(get_db)
):
    # Verify customer exists
    customer = crud.get_customer(db, application.customer_id)
    if not customer:
        raise HTTPException(
            status_code=400,
            detail="Customer not found"
        )
    
    # Verify branch exists
    branch = crud.get_branch(db, application.branch_id)
    if not branch:
        raise HTTPException(
            status_code=400,
            detail="Branch not found"
        )
    
    # Verify department exists
    department = crud.get_department(db, application.department_id)
    if not department:
        raise HTTPException(
            status_code=400,
            detail="Department not found"
        )
    
    # Verify creating user exists
    user = crud.get_user(db, created_by_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Creating user not found"
        )
    
    return crud.create_loan_application(db=db, application=application, created_by_id=created_by_id)

@router.get("/loan-applications/", response_model=List[schemas.LoanApplicationResponse])
def read_loan_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by application status"),
    loan_type: Optional[str] = Query(None, description="Filter by loan type"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    assigned_officer_id: Optional[str] = Query(None, description="Filter by assigned officer"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db)
):
    applications = crud.get_loan_applications(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        loan_type=loan_type,
        customer_id=customer_id,
        assigned_officer_id=assigned_officer_id,
        branch_id=branch_id
    )
    return applications

@router.get("/loan-applications/{application_id}", response_model=schemas.LoanApplicationResponse)
def read_loan_application(application_id: str, db: Session = Depends(get_db)):
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return db_application

@router.put("/loan-applications/{application_id}", response_model=schemas.LoanApplicationResponse)
def update_loan_application(
    application_id: str, 
    application: schemas.LoanApplicationUpdate, 
    db: Session = Depends(get_db)
):
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Optimistic locking check
    if db_application.version != application.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Loan application has been updated by another process. Please refresh and try again."
        )
    
    # Only allow updates if application is in draft or submitted status
    if db_application.status not in [models.LoanStatus.draft, models.LoanStatus.submitted]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update application in {db_application.status.value} status"
        )
    
    updated_application = crud.update_loan_application(db=db, application_id=application_id, application=application)
    return updated_application

@router.patch("/loan-applications/{application_id}/status", response_model=schemas.LoanApplicationResponse)
def update_loan_application_status(
    application_id: str,
    status_update: schemas.LoanApplicationStatusUpdate,
    updated_by_id: str = Query(..., description="ID of the user updating the status"),
    db: Session = Depends(get_db)
):
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Optimistic locking check
    if db_application.version != status_update.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Loan application has been updated by another process. Please refresh and try again."
        )
    
    # Verify updating user exists
    user = crud.get_user(db, updated_by_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Updating user not found"
        )
    
    # Validate status transitions
    current_status = db_application.status
    new_status = status_update.status
    
    valid_transitions = {
        models.LoanStatus.draft: [models.LoanStatus.submitted],
        models.LoanStatus.submitted: [models.LoanStatus.under_review, models.LoanStatus.rejected],
        models.LoanStatus.under_review: [models.LoanStatus.approved, models.LoanStatus.rejected],
        models.LoanStatus.approved: [models.LoanStatus.disbursed],
        models.LoanStatus.disbursed: [models.LoanStatus.closed],
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status.value} to {new_status.value}"
        )
    
    # Additional validations for specific status updates
    if new_status == models.LoanStatus.approved and not status_update.interest_rate:
        raise HTTPException(
            status_code=400,
            detail="Interest rate is required for loan approval"
        )
    
    if new_status == models.LoanStatus.rejected and not status_update.rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required for loan rejection"
        )
    
    updated_application = crud.update_loan_application_status(
        db=db, 
        application_id=application_id, 
        status_update=status_update,
        updated_by_id=updated_by_id
    )
    return updated_application

@router.patch("/loan-applications/{application_id}/assign-officer")
def assign_loan_officer(
    application_id: str,
    officer_id: str = Query(..., description="ID of the officer to assign"),
    db: Session = Depends(get_db)
):
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Verify officer exists and has appropriate role
    officer = crud.get_user(db, officer_id)
    if not officer:
        raise HTTPException(
            status_code=400,
            detail="Officer not found"
        )
    
    if officer.role not in [models.UserRole.officer, models.UserRole.manager, models.UserRole.admin]:
        raise HTTPException(
            status_code=400,
            detail="User does not have appropriate role for loan processing"
        )
    
    updated_application = crud.assign_loan_officer(db=db, application_id=application_id, officer_id=officer_id)
    return {"message": "Officer assigned successfully", "assigned_officer_id": officer_id}

@router.delete("/loan-applications/{application_id}", response_model=schemas.LoanApplicationResponse)
def delete_loan_application(application_id: str, db: Session = Depends(get_db)):
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Only allow deletion if application is in draft status
    if db_application.status != models.LoanStatus.draft:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete application in {db_application.status.value} status"
        )
    
    deleted_application = crud.delete_loan_application(db=db, application_id=application_id)
    return deleted_application

# Loan Documents endpoints
@router.get("/loan-applications/{application_id}/documents", response_model=List[schemas.LoanDocumentResponse])
def get_loan_documents(application_id: str, db: Session = Depends(get_db)):
    # Verify application exists
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    documents = crud.get_loan_documents(db, application_id=application_id)
    return documents

@router.post("/loan-applications/{application_id}/documents", response_model=schemas.LoanDocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_loan_document(
    application_id: str,
    document_type: str = Form(...),
    document_name: str = Form(...),
    uploaded_by_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify application exists
    db_application = crud.get_loan_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Save file
    upload_dir = Path("uploads") / "loan-documents" / application_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Create document record
    document_data = schemas.LoanDocumentCreate(
        loan_application_id=application_id,
        document_type=document_type,
        document_name=document_name,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by_id=uploaded_by_id
    )
    
    return crud.create_loan_document(db=db, document=document_data)

@router.patch("/loan-documents/{document_id}/verify", response_model=schemas.LoanDocumentResponse)
def verify_loan_document(
    document_id: str,
    verification_data: schemas.LoanDocumentUpdate,
    verified_by_id: str = Query(..., description="ID of the user verifying the document"),
    db: Session = Depends(get_db)
):
    db_document = crud.get_loan_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify verifying user exists
    user = crud.get_user(db, verified_by_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Verifying user not found"
        )
    
    updated_document = crud.update_loan_document(
        db=db, 
        document_id=document_id, 
        document=verification_data,
        verified_by_id=verified_by_id
    )
    return updated_document

@router.delete("/loan-documents/{document_id}", response_model=schemas.LoanDocumentResponse)
def delete_loan_document(document_id: str, db: Session = Depends(get_db)):
    db_document = crud.get_loan_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    try:
        if os.path.exists(db_document.file_path):
            os.remove(db_document.file_path)
    except Exception as e:
        # Log error but don't fail the operation
        pass
    
    deleted_document = crud.delete_loan_document(db=db, document_id=document_id)
    return deleted_document

# Loan calculation endpoints
@router.post("/loan-calculations/emi", response_model=schemas.LoanCalculationResponse)
def calculate_loan_emi(calculation_request: schemas.LoanCalculationRequest):
    """Calculate EMI and generate loan schedule"""
    monthly_emi = crud.calculate_emi(
        calculation_request.loan_amount,
        calculation_request.interest_rate,
        calculation_request.loan_tenure_months
    )
    
    total_amount = monthly_emi * calculation_request.loan_tenure_months
    total_interest = total_amount - calculation_request.loan_amount
    
    emi_schedule = crud.generate_emi_schedule(
        calculation_request.loan_amount,
        calculation_request.interest_rate,
        calculation_request.loan_tenure_months
    )
    
    return schemas.LoanCalculationResponse(
        loan_amount=calculation_request.loan_amount,
        interest_rate=calculation_request.interest_rate,
        loan_tenure_months=calculation_request.loan_tenure_months,
        monthly_emi=monthly_emi,
        total_interest=round(total_interest, 2),
        total_amount=round(total_amount, 2),
        emi_schedule=emi_schedule
    )

# Statistics and reporting endpoints
@router.get("/loan-applications/stats/summary", response_model=schemas.LoanSummaryStats)
def get_loan_summary_statistics(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    db: Session = Depends(get_db)
):
    """Get summary statistics for loan applications"""
    stats = crud.get_loan_summary_stats(db, branch_id=branch_id)
    return schemas.LoanSummaryStats(**stats)