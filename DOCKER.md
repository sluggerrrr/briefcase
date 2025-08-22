# Docker Setup for Briefcase Application

This document describes the Docker configuration for the Briefcase secure document sharing application.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start (Development)

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd file-sharing-app
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize database:**
   ```bash
   # Run migrations
   docker-compose exec backend .venv/bin/alembic upgrade head
   
   # Seed test data
   docker-compose exec backend .venv/bin/python seed_db.py
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Services

### Backend (FastAPI)
- **Port:** 8000
- **Technology:** Python 3.12 + FastAPI + uv
- **Features:** JWT auth, AES encryption, document management
- **Health Check:** `/health` endpoint

### Frontend (Next.js)
- **Port:** 3000  
- **Technology:** Next.js + TypeScript + Tailwind CSS
- **Features:** Document dashboard, authentication UI

### Database (PostgreSQL)
- **Port:** 5432
- **Version:** PostgreSQL 15
- **Database:** briefcase_dev
- **User:** briefcase_user

## Docker Compose Files

### `docker-compose.yml` (Development)
- Includes hot-reload for both frontend and backend
- Uses development database credentials
- Mounts source code as volumes for live editing
- Includes health checks and dependency management

### `docker-compose.prod.yml` (Production)
- Optimized production builds
- Includes Nginx reverse proxy
- Uses environment variables for configuration
- Security-hardened settings

## Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://briefcase_user:briefcase_password@db:5432/briefcase_dev
POSTGRES_PASSWORD=briefcase_password

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Application
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

### Starting Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend
```

### Backend Development
```bash
# Install new dependencies
docker-compose exec backend uv add package-name

# Run migrations
docker-compose exec backend .venv/bin/alembic upgrade head

# Create new migration
docker-compose exec backend .venv/bin/alembic revision --autogenerate -m "Description"

# Run tests
docker-compose exec backend .venv/bin/pytest

# Access backend shell
docker-compose exec backend bash
```

### Frontend Development
```bash
# Install new dependencies
docker-compose exec frontend npm install package-name

# Access frontend shell
docker-compose exec frontend sh
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec db psql -U briefcase_user -d briefcase_dev

# Backup database
docker-compose exec db pg_dump -U briefcase_user briefcase_dev > backup.sql

# Restore database
docker-compose exec -T db psql -U briefcase_user briefcase_dev < backup.sql
```

## Production Deployment

1. **Prepare environment:**
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with production values
   ```

2. **Deploy with production compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Initialize production database:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend .venv/bin/alembic upgrade head
   ```

## Security Considerations

### Development
- Uses development credentials (change in production)
- Debug mode enabled
- CORS allows localhost origins

### Production
- Environment variables for all sensitive data
- Non-root users in containers
- Nginx reverse proxy with security headers
- Production-optimized builds
- Disabled debug modes

## Troubleshooting

### Common Issues

1. **Database connection failed:**
   ```bash
   # Check database health
   docker-compose exec db pg_isready -U briefcase_user
   
   # Check logs
   docker-compose logs db
   ```

2. **Backend startup errors:**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Verify environment variables
   docker-compose exec backend env | grep DATABASE_URL
   ```

3. **Frontend build issues:**
   ```bash
   # Clear node_modules and reinstall
   docker-compose down
   docker-compose up --build frontend
   ```

4. **Port conflicts:**
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :5432
   ```

### Clean Reset
```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Rebuild everything
docker-compose up --build -d
```

## Performance Optimization

### Development
- Use volume mounts for hot-reload
- Leverage Docker layer caching
- Use `.dockerignore` to exclude unnecessary files

### Production
- Multi-stage builds for smaller images
- Health checks for proper orchestration
- Resource limits and restart policies
- Nginx for static file serving and compression

## Monitoring and Logs

```bash
# Monitor all services
docker-compose logs -f

# Monitor specific service
docker-compose logs -f backend

# Check resource usage
docker stats

# Health check status
docker-compose ps
```