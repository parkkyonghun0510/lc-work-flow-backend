from fastapi import FastAPI

app = FastAPI(
    title="Loan Application Backend",
    description="API for managing loan applications, users, branches, and departments.",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Loan Application API!"}

from app.api import customer as customer_api
from app.api import auth as auth_api

# Include API routers here as they are developed
app.include_router(customer_api.router, prefix="/api", tags=["Customers"])
app.include_router(auth_api.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(users_router, prefix="/users", tags=["Users"])
# app.include_router(branches_router, prefix="/branches", tags=["Branches"])
# app.include_router(departments_router, prefix="/departments", tags=["Departments"])