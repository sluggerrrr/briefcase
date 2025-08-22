# Backend Dockerfile for Briefcase application
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --no-dev

# Development stage
FROM base as development

# Install development dependencies
RUN . .venv/bin/activate && uv sync

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Set environment variables for development
ENV DEBUG=true
ENV DATABASE_URL=postgresql://user:password@db:5432/briefcase_dev
ENV SECRET_KEY=dev-secret-key-change-in-production
ENV ENCRYPTION_KEY=dev-encryption-key-change-in-production

# Run development server
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create non-root user
RUN useradd --create-home --shell /bin/bash briefcase
RUN chown -R briefcase:briefcase /app
USER briefcase

# Expose port
EXPOSE 8000

# Run production server
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]