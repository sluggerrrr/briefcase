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

Project setup and API specifications to be defined.