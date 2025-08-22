# Backend - File Sharing API

Backend service for the file sharing application.

## Tech Stack

- **Runtime**: Python 3.9+
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT tokens
- **File Storage**: Local filesystem
- **Package Manager**: uv

## Project Structure

```
apps/backend/
├── app/                  # Main application code
├── pyproject.toml       # Project configuration and dependencies
├── .env                 # Environment variables
└── CLAUDE.md           # This file
```

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- uv (https://docs.astral.sh/uv/)

### Setup with uv
```bash
# Initialize Python project
uv init

# Add dependencies (when needed)
uv add fastapi uvicorn sqlalchemy psycopg2-binary

# Activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run development server (when main.py is created)
uv run uvicorn app.main:app --reload
```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/filedb
SECRET_KEY=your-secret-key
```

## Development

### Running Tests

The project uses pytest for testing with proper test isolation and fixtures.

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py

# Run specific test class or function
uv run pytest tests/test_auth.py::TestUserLogin
uv run pytest tests/test_auth.py::TestUserLogin::test_login_valid_credentials

# Run tests with coverage (when coverage is added)
uv run pytest --cov=app tests/
```

### Test Structure

- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_auth.py` - Authentication system tests
- Uses SQLite in-memory database for test isolation
- Automated test fixtures for user registration and authentication

### Development Workflow

1. Write tests first (TDD approach)
2. Implement functionality to pass tests
3. Run tests to verify implementation
4. Refactor if needed while keeping tests green