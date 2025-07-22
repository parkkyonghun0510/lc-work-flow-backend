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

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Update the `.env` file with your database credentials:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/le-db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
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

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}` - Get customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

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

## 🚀 Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Environment Variables

Make sure to set these environment variables in production:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Strong secret key for JWT tokens
- `ENVIRONMENT`: Set to "production"
- `DEBUG`: Set to "false"

## 📄 License

This project is licensed under the MIT License.