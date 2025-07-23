from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import SessionLocal
import os
import uuid
from typing import List
import shutil
from pathlib import Path

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/jpg", "image/png", 
    "application/pdf", 
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_file(file: UploadFile) -> bool:
    """Validate file type and size"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"MIME type not allowed. File type: {file.content_type}"
        )
    
    return True

def save_file(file: UploadFile, subfolder: str = "") -> str:
    """Save uploaded file and return the file path"""
    # Create upload directory if it doesn't exist
    upload_path = Path(UPLOAD_DIR)
    if subfolder:
        upload_path = upload_path / subfolder
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_path / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return str(file_path)

@router.post("/upload/id-card", status_code=status.HTTP_201_CREATED)
async def upload_id_card(
    customer_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload ID card image for a customer"""
    # Validate file
    validate_file(file)
    
    # Check if it's an image file for ID cards
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="ID card uploads must be image files"
        )
    
    # Save file in id-cards subfolder
    try:
        file_path = save_file(file, "id-cards")
        
        return {
            "message": "ID card uploaded successfully",
            "file_path": file_path,
            "customer_id": customer_id,
            "original_filename": file.filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/upload/document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    document_type: str = Form(...),
    customer_id: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload general documents"""
    # Validate file
    validate_file(file)
    
    # Save file in documents subfolder
    try:
        file_path = save_file(file, "documents")
        
        return {
            "message": "Document uploaded successfully",
            "file_path": file_path,
            "document_type": document_type,
            "customer_id": customer_id,
            "original_filename": file.filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/upload/multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    customer_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple files at once"""
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per upload"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Validate each file
            validate_file(file)
            
            # Determine subfolder based on file type
            subfolder = "images" if file.content_type.startswith("image/") else "documents"
            file_path = save_file(file, subfolder)
            
            uploaded_files.append({
                "original_filename": file.filename,
                "file_path": file_path,
                "content_type": file.content_type
            })
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "message": f"Upload completed. {len(uploaded_files)} files uploaded successfully.",
        "customer_id": customer_id,
        "uploaded_files": uploaded_files,
        "failed_files": failed_files
    }

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download a file by its path"""
    full_path = Path(UPLOAD_DIR) / file_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    if not full_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Path is not a file"
        )
    
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
        media_type='application/octet-stream'
    )

@router.delete("/delete/{file_path:path}", status_code=status.HTTP_200_OK)
async def delete_file(file_path: str):
    """Delete a file by its path"""
    full_path = Path(UPLOAD_DIR) / file_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    try:
        full_path.unlink()
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.get("/info")
async def get_upload_info():
    """Get upload configuration information"""
    return {
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "allowed_mime_types": list(ALLOWED_MIME_TYPES),
        "upload_directory": UPLOAD_DIR
    }