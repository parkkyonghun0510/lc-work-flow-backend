import os
from fastapi import FastAPI
from app.middleware import setup_middleware

app = FastAPI(
    title="Loan Application Backend",
    description="API for managing loan applications, users, branches, and departments.",
    version="0.1.0",
)

# Setup middleware
setup_middleware(app)

@app.get("/")
async def root():
    return {"message": "Welcome to the Loan Application API!"}

from app.api import customer as customer_api
from app.api import auth as auth_api
from app.api import user as user_api
from app.api import branch as branch_api
from app.api import department as department_api
from app.api import upload as upload_api
from app.api import health as health_api
from app.api import loan as loan_api

# Include API routers
app.include_router(customer_api.router, prefix="/api", tags=["Customers"])
app.include_router(auth_api.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_api.router, prefix="/api", tags=["Users"])
app.include_router(branch_api.router, prefix="/api", tags=["Branches"])
app.include_router(department_api.router, prefix="/api", tags=["Departments"])
app.include_router(upload_api.router, prefix="/api", tags=["File Upload"])
app.include_router(health_api.router, prefix="/api", tags=["Health Check"])
app.include_router(loan_api.router, prefix="/api", tags=["Loans"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)