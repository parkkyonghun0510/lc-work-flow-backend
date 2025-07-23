# LC Work Flow Backend

FastAPI backend for the LC Work Flow loan application system.

## 🚀 Quick Setup

### Prerequisites

1. **Python 3.9+** installed
2. **PostgreSQL** database running
3. **Redis** server running (optional, for caching)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with default values. Update if needed:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:123456@localhost:5432/le-db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-lc-workflow-2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Setup Database

Run the setup script to create tables and test users:

```bash
python setup_backend.py
```

This will:
- Create all database tables
- Create default branch and department
- Create test users with different roles

### 4. Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test Authentication

```bash
python test_auth.py
```

## 📋 Test Users

The setup script creates these test users:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full system access |
| `manager` | `manager123` | Manager | Management functions |
| `officer` | `officer123` | Officer | Loan processing |
| `testuser` | `testpassword` | Admin | Legacy test user |

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/token` - Login (OAuth2 compatible)

### Users Management
- `GET /api/users/` - List users (with filters)
- `POST /api/users/` - Create user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/change-password` - Change user password

### Branches Management
- `GET /api/branches/` - List branches (with filters)
- `POST /api/branches/` - Create branch
- `GET /api/branches/{id}` - Get branch details
- `PUT /api/branches/{id}` - Update branch
- `DELETE /api/branches/{id}` - Delete branch
- `GET /api/branches/active` - Get active branches

### Departments Management
- `GET /api/departments/` - List departments (with filters)
- `POST /api/departments/` - Create department
- `GET /api/departments/{id}` - Get department details
- `PUT /api/departments/{id}` - Update department
- `DELETE /api/departments/{id}` - Delete department
- `GET /api/departments/active` - Get active departments

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}` - Get customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Loan Applications
- `GET /api/loan-applications/` - List loan applications (with filters)
- `POST /api/loan-applications/` - Create loan application
- `GET /api/loan-applications/{id}` - Get loan application details
- `PUT /api/loan-applications/{id}` - Update loan application
- `DELETE /api/loan-applications/{id}` - Delete loan application (draft only)
- `PATCH /api/loan-applications/{id}/status` - Update application status
- `PATCH /api/loan-applications/{id}/assign-officer` - Assign loan officer
- `GET /api/loan-applications/stats/summary` - Get loan statistics

### Loan Documents
- `GET /api/loan-applications/{id}/documents` - Get loan documents
- `POST /api/loan-applications/{id}/documents` - Upload loan document
- `PATCH /api/loan-documents/{id}/verify` - Verify document
- `DELETE /api/loan-documents/{id}` - Delete document

### Loan Calculations
- `POST /api/loan-calculations/emi` - Calculate EMI and loan schedule

### File Upload
- `POST /api/upload/id-card` - Upload ID card image
- `POST /api/upload/document` - Upload general document
- `POST /api/upload/multiple` - Upload multiple files
- `GET /api/upload/download/{filename}` - Download file
- `DELETE /api/upload/delete/{filename}` - Delete file
- `GET /api/upload/info` - Get upload configuration

### Health Checks
- `GET /api/health/` - Basic health check
- `GET /api/health/detailed` - Detailed health with metrics
- `GET /api/health/database` - Database health check
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

## 📖 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Development

### Database Reset

To reset the database:

```bash
# Drop and recreate tables
python -c "from app.database import engine, Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Recreate test data
python setup_backend.py
```

### Testing

```bash
# Test authentication
python test_auth.py

# Test customer API
python test_customer_api.py
```

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. **Login**: Send username/password to `/api/auth/token`
2. **Get Token**: Receive JWT access token
3. **Use Token**: Include in Authorization header: `Bearer <token>`

### Example Login Request

```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Example Authenticated Request

```bash
curl -X GET "http://localhost:8000/api/customers/" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## 🐛 Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Create database if it doesn't exist:
   ```sql
   CREATE DATABASE le_db;
   ```

### Redis Connection Issues

1. Ensure Redis is running
2. Check Redis URL in `.env`
3. Redis is optional - comment out Redis imports if not needed

### Authentication Issues

1. Run `python test_auth.py` to verify setup
2. Check JWT secret key in `.env`
3. Ensure test users were created with `python setup_backend.py`

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── crud/          # Database operations
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── auth_utils.py  # JWT utilities
│   └── database.py    # Database configuration
├── main.py            # FastAPI application
├── setup_backend.py   # Database setup script
├── test_auth.py       # Authentication tests
└── requirements.txt   # Python dependencies
```
