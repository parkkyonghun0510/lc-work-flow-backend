from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import SessionLocal, engine
from datetime import datetime
import psutil
import os

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Loan Application Backend",
        "version": "0.1.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database and system metrics"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Loan Application Backend",
        "version": "0.1.0",
        "checks": {}
    }
    
    # Database health check
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": disk.percent,
            "available_memory_mb": memory.available // (1024 * 1024),
            "available_disk_gb": disk.free // (1024 * 1024 * 1024)
        }
        
        # Mark as unhealthy if resources are critically low
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["checks"]["system"]["status"] = "degraded"
            health_status["checks"]["system"]["message"] = "High resource usage detected"
            
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unknown",
            "message": f"Could not retrieve system metrics: {str(e)}"
        }
    
    # Upload directory check
    try:
        upload_dir = "uploads"
        if os.path.exists(upload_dir) and os.path.isdir(upload_dir):
            health_status["checks"]["upload_directory"] = {
                "status": "healthy",
                "message": "Upload directory accessible",
                "path": os.path.abspath(upload_dir)
            }
        else:
            health_status["checks"]["upload_directory"] = {
                "status": "warning",
                "message": "Upload directory not found",
                "path": os.path.abspath(upload_dir)
            }
    except Exception as e:
        health_status["checks"]["upload_directory"] = {
            "status": "unhealthy",
            "message": f"Upload directory check failed: {str(e)}"
        }
    
    return health_status

@router.get("/health/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Specific database health check with connection pool info"""
    try:
        # Test basic query
        result = db.execute(text("SELECT version()"))
        db_version = result.scalar()
        
        # Test table access
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        customer_count = db.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        branch_count = db.execute(text("SELECT COUNT(*) FROM branches")).scalar()
        department_count = db.execute(text("SELECT COUNT(*) FROM departments")).scalar()
        
        # Connection pool info
        pool = engine.pool
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_version": db_version,
            "table_counts": {
                "users": user_count,
                "customers": customer_count,
                "branches": branch_count,
                "departments": department_count
            },
            "connection_pool": {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness probe"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Check if upload directory exists
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/health/live")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"status": "alive"}