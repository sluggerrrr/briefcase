# 🚀 Backend - Briefcase Document Sharing API

Secure, enterprise-grade backend service for the Briefcase document sharing platform, built with FastAPI and featuring comprehensive security, permission management, and document lifecycle automation.

## 🚀 Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
```

**API Server**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs  
**Admin Interface**: http://localhost:8000/redoc

## 📦 Technology Stack

### Core Framework
- **FastAPI 0.104+** - Modern Python web framework
- **Python 3.9+** - Latest Python with type hints
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic v2** - Data validation using Python types

### Database & Storage
- **SQLAlchemy 2.0** - Modern Python SQL toolkit and ORM
- **PostgreSQL** - Production database (SQLite for development)
- **Alembic** - Database migration management
- **asyncpg** - Fast PostgreSQL adapter

### Security & Authentication
- **JWT Tokens** - Secure authentication with refresh tokens
- **bcrypt** - Password hashing with salt
- **AES-256 Encryption** - Document encryption at rest
- **RBAC** - Role-based access control system
- **CORS** - Cross-origin resource sharing configuration

### Development & Testing
- **pytest** - Comprehensive testing framework
- **uv** - Ultra-fast Python package manager
- **SQLite** - In-memory database for testing
- **Coverage.py** - Test coverage reporting

## 🏗️ Project Structure

```
apps/backend/
├── app/                          # Main application code
│   ├── api/                      # API routes and endpoints
│   │   ├── dependencies.py       # Common dependencies
│   │   └── v1/                   # API version 1
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── documents.py      # Document management
│   │       ├── documents_enhanced.py # Advanced document features
│   │       ├── permissions.py    # Permission management
│   │       ├── admin.py          # Admin endpoints
│   │       ├── admin_enhanced.py # Advanced admin features
│   │       ├── users.py          # User management
│   │       ├── document_status.py # Document status tracking
│   │       └── document_status_enhanced.py # Advanced status features
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Application configuration
│   │   ├── database.py           # Database connection and setup
│   │   ├── security.py           # Security utilities
│   │   └── encryption.py         # Document encryption service
│   ├── models/                   # SQLAlchemy data models
│   │   ├── user.py               # User model
│   │   ├── document.py           # Document model
│   │   ├── permissions.py        # Permission models
│   │   └── lifecycle.py          # Lifecycle management models
│   ├── schemas/                  # Pydantic schemas
│   │   ├── auth.py               # Authentication schemas
│   │   ├── document.py           # Document schemas
│   │   ├── permissions.py        # Permission schemas
│   │   └── lifecycle.py          # Lifecycle schemas
│   ├── services/                 # Business logic services
│   │   ├── document_service.py   # Document business logic
│   │   ├── permission_service.py # Permission management
│   │   ├── lifecycle_service.py  # Document lifecycle automation
│   │   └── encryption_service.py # Encryption/decryption service
│   ├── dependencies/             # Dependency injection
│   │   └── permissions.py        # Permission dependencies
│   └── main.py                   # FastAPI application entry point
├── tests/                        # Test suite
│   ├── conftest.py               # Test configuration and fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_documents.py         # Document management tests
│   ├── test_permissions.py       # Permission system tests
│   └── test_lifecycle_service.py # Lifecycle management tests
├── alembic/                      # Database migrations
├── pyproject.toml                # Project configuration and dependencies
├── .env.example                  # Example environment variables
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables
Create `.env` file based on `.env.example`:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/briefcase_db
# For development, use SQLite: sqlite:///./briefcase_dev.db

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Storage Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Document Encryption
ENCRYPTION_KEY=your-32-character-encryption-key

# Admin Configuration
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure-admin-password

# Optional: Lifecycle Management
LIFECYCLE_CHECK_INTERVAL=3600  # 1 hour
CLEANUP_BATCH_SIZE=100
```

### Database Setup
```bash
# Install PostgreSQL (optional, SQLite works for development)
# Create database
createdb briefcase_db

# Run database migrations
uv run alembic upgrade head

# Create admin user (development)
uv run python -m app.scripts.create_admin
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Access and refresh token system
- **Password Hashing**: bcrypt with salt rounds
- **Role-Based Access**: Admin, Owner, Editor, Viewer roles
- **Permission System**: Granular document permissions
- **Session Management**: Secure token lifecycle

### Document Security
- **AES-256 Encryption**: All documents encrypted at rest
- **Access Control**: Document-level permission checks
- **Audit Logging**: Complete access trail for compliance
- **Time-based Access**: Document expiration and view limits
- **Secure Download**: Temporary URLs and access validation

### API Security
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **CORS Configuration**: Proper cross-origin handling
- **Rate Limiting**: Protection against abuse (planned)
- **Request Size Limits**: File upload size restrictions

## 📊 API Endpoints

### Authentication (`/api/v1/auth`)
```
POST   /login              # User authentication
POST   /register           # User registration
POST   /refresh            # Token refresh
POST   /logout             # User logout
GET    /me                 # Current user info
```

### Document Management (`/api/v1/documents`)
```
GET    /                   # List user documents
POST   /                   # Upload new document
GET    /{id}               # Get document info
PUT    /{id}               # Update document
DELETE /{id}               # Delete document
GET    /{id}/download      # Download document
GET    /{id}/content       # Get document content

# Enhanced Document Operations
GET    /accessible         # List accessible documents
GET    /search             # Advanced document search
POST   /bulk/delete        # Bulk delete operations
POST   /bulk/share         # Bulk sharing operations
POST   /bulk/download      # Bulk download as ZIP
```

### Permission Management (`/api/v1/permissions`)
```
GET    /users/me/permissions              # Get current user permissions
GET    /users/{id}/permissions           # Get user permissions
GET    /documents/{id}/permissions       # Get document permissions
POST   /documents/{id}/permissions       # Grant document permission
DELETE /documents/{id}/permissions       # Revoke document permission
POST   /documents/bulk/permissions/grant # Bulk permission operations
POST   /permissions/check                # Check multiple permissions
```

### User Management (`/api/v1/users`)
```
GET    /                   # List users (admin)
GET    /me                 # Get current user profile
PUT    /me/password        # Update password
```

### Document Status (`/api/v1/documents/{id}/status`)
```
GET    /                   # Get document status
GET    /history            # Get status history
GET    /analytics          # Get document analytics
GET    /health             # Document health check
POST   /bulk               # Bulk status check
```

### Admin Operations (`/api/v1/admin`)
```
GET    /lifecycle/status   # Lifecycle system status
POST   /lifecycle/run-cleanup # Manual cleanup trigger
GET    /lifecycle/config   # Get lifecycle configuration
PUT    /lifecycle/config/{setting} # Update configuration
GET    /lifecycle/jobs     # Cleanup job history
GET    /permissions/overview # Permission system overview
POST   /permissions/initialize # Initialize permissions
```

### System Monitoring
```
GET    /admin/status/overview # System status overview
GET    /admin/status/health   # System health check
GET    /admin/status/metrics  # Performance metrics
```

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── conftest.py                # Test fixtures and configuration
├── test_auth.py               # Authentication system tests
├── test_documents.py          # Document management tests
├── test_permissions.py        # Permission system tests
├── test_lifecycle_service.py  # Lifecycle automation tests
├── test_admin.py              # Admin functionality tests
└── test_integration.py        # End-to-end integration tests
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run tests in parallel (faster)
uv run pytest -n auto

# Run only failing tests
uv run pytest --lf
```

### Test Features
- **Isolated Testing**: Each test uses fresh database
- **Comprehensive Fixtures**: Automated test data setup
- **Permission Testing**: Complete RBAC validation
- **Security Testing**: Authentication and authorization
- **Integration Testing**: End-to-end API workflows

## 🔄 Database Management

### Migrations with Alembic
```bash
# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# View migration history
uv run alembic history

# Check current revision
uv run alembic current
```

### Database Models
```python
# User model with roles
class User(Base):
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))
    created_at = Column(DateTime)

# Document model with encryption
class Document(Base):
    id = Column(UUID, primary_key=True)
    title = Column(String)
    encrypted_content = Column(LargeBinary)
    encryption_key = Column(String)
    sender_id = Column(UUID, ForeignKey("users.id"))
    status = Column(Enum(DocumentStatus))
    expires_at = Column(DateTime)
```

## 🚀 Performance & Scalability

### Database Optimization
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed columns and efficient queries
- **Lazy Loading**: Relationships loaded on demand
- **Pagination**: Large result set handling
- **Caching**: Strategic caching for frequently accessed data

### File Handling
- **Streaming**: Large file upload/download streaming
- **Async Operations**: Non-blocking I/O operations
- **Memory Management**: Efficient file processing
- **Base64 Handling**: Optimized encoding/decoding
- **Cleanup Jobs**: Automated file cleanup and maintenance

### API Performance
- **Async FastAPI**: Non-blocking request handling
- **Pydantic v2**: Fast data validation and serialization
- **Dependency Injection**: Efficient resource management
- **Background Tasks**: Async task processing
- **Response Compression**: Gzip compression for large responses

## 🔧 Development Tools

### Available Scripts
```bash
# Development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest                    # All tests
uv run pytest -v                # Verbose output
uv run pytest --cov=app         # With coverage
uv run pytest -x                # Stop on first failure
uv run pytest --lf              # Last failed tests

# Database operations
uv run alembic upgrade head      # Apply migrations
uv run alembic revision --autogenerate -m "message"  # Create migration

# Code quality
uv run black app/                # Code formatting
uv run isort app/                # Import sorting
uv run flake8 app/               # Linting
uv run mypy app/                 # Type checking

# Admin utilities
uv run python -m app.scripts.create_admin    # Create admin user
uv run python -m app.scripts.seed_data       # Seed test data
uv run python -m app.scripts.cleanup_files   # Manual file cleanup
```

### Development Workflow
1. **Feature Development**: Create feature branch
2. **Test-Driven Development**: Write tests first
3. **Implementation**: Implement feature to pass tests
4. **Code Quality**: Run linting and type checking
5. **Testing**: Ensure all tests pass
6. **Documentation**: Update API documentation
7. **Code Review**: Submit PR for review

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
uv sync --no-dev

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/briefcase_prod"
export SECRET_KEY="your-production-secret-key"

# Run database migrations
uv run alembic upgrade head

# Start production server
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Environment Configuration
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@db-host:5432/briefcase_prod
SECRET_KEY=your-super-secret-production-key
CORS_ORIGINS=["https://yourdomain.com"]
UPLOAD_DIR=/app/uploads
```

## 🔍 Monitoring & Logging

### Application Logging
```python
import logging
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/admin/status/health

# System metrics
curl http://localhost:8000/admin/status/metrics
```

### Performance Monitoring
- **Response Times**: API endpoint performance tracking
- **Database Queries**: Slow query identification
- **Memory Usage**: Application memory monitoring
- **Error Rates**: Exception and error tracking
- **Security Events**: Authentication and permission failures

## 🔍 Troubleshooting

### Common Issues

**Database Connection Issues**
```bash
# Check database connection
uv run python -c "from app.core.database import engine; print(engine.url)"

# Test database connectivity
uv run python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('Connected!')"
```

**Migration Issues**
```bash
# Reset migrations (development only)
uv run alembic downgrade base
uv run alembic upgrade head

# Check migration status
uv run alembic current
uv run alembic history
```

**Authentication Problems**
```bash
# Verify JWT secret
uv run python -c "from app.core.config import settings; print(f'Secret: {settings.SECRET_KEY[:10]}...')"

# Test token generation
uv run python -c "from app.core.security import create_access_token; print(create_access_token({'sub': 'test'}))"
```

**File Upload Issues**
```bash
# Check upload directory permissions
ls -la ./uploads/

# Verify file size limits
uv run python -c "from app.core.config import settings; print(f'Max size: {settings.MAX_FILE_SIZE}')"
```

## 📚 Additional Resources

### FastAPI & Python
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **Pydantic Documentation**: https://docs.pydantic.dev
- **uv Package Manager**: https://docs.astral.sh/uv/

### Security Resources
- **JWT Best Practices**: https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/
- **Python Security**: https://python-security.readthedocs.io
- **OWASP API Security**: https://owasp.org/www-project-api-security/

### Database & ORM
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Alembic Documentation**: https://alembic.sqlalchemy.org
- **Database Design**: https://www.postgresql.org/docs/current/ddl.html

## 🤝 Contributing

See the main project [README.md](../../README.md) for contribution guidelines.

### Code Standards
- **PEP 8**: Python code style guidelines
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Google-style docstrings for functions
- **Testing**: Test coverage >90% for all new code
- **Security**: Security review for all authentication/permission changes

---

**Built with Python and FastAPI for enterprise-grade document security and management.**