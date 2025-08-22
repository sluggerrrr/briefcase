# Deployment Guide

This guide covers deploying the file sharing application with the backend on Railway and frontend on Vercel.

## Architecture Overview

- **Backend**: FastAPI application hosted on Railway
- **Frontend**: Next.js application hosted on Vercel  
- **Database**: PostgreSQL hosted on Railway
- **File Storage**: Railway volume storage

## Backend Deployment (Railway)

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account
3. Install Railway CLI: `npm install -g @railway/cli`

### 2. Deploy Backend
```bash
# Login to Railway
railway login

# Navigate to backend directory
cd apps/backend

# Initialize Railway project
railway init

# Add PostgreSQL database
railway add postgresql

# Deploy the application
railway up
```

### 3. Configure Environment Variables
In Railway dashboard, set these environment variables:

```env
# Database (automatically provided by Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database

# Security
SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (replace with your Vercel domain)
ALLOWED_ORIGINS=["https://your-frontend.vercel.app", "http://localhost:3000"]

# File Storage
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=100  # MB

# Encryption
ENCRYPTION_SECRET=your-32-character-encryption-key
```

### 4. Set Custom Domain (Optional)
1. In Railway dashboard, go to your service
2. Click "Settings" → "Domains"
3. Add custom domain or use Railway subdomain

## Frontend Deployment (Vercel)

### 1. Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub account
3. Install Vercel CLI: `npm install -g vercel`

### 2. Deploy Frontend
```bash
# Navigate to frontend directory
cd apps/frontend

# Login to Vercel
vercel login

# Deploy the application
vercel

# Follow the prompts:
# - Link to existing project? No
# - Project name: file-sharing-frontend
# - Directory: ./
# - Override settings? No
```

### 3. Configure Environment Variables
In Vercel dashboard, set these environment variables:

```env
# API Configuration (replace with your Railway URL)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=Briefcase

# Optional: Analytics and monitoring
VERCEL_ANALYTICS_ID=your-analytics-id
```

### 4. Set Production Domain
1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain

## Database Migration

### Railway PostgreSQL Setup
```bash
# Connect to Railway PostgreSQL
railway connect postgresql

# Run migrations (from backend directory)
cd apps/backend
uv run alembic upgrade head

# Create initial admin user (optional)
uv run python -c "
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate

db = next(get_db())
user_service = UserService(db)
admin_user = UserCreate(
    email='admin@briefcase.com',
    password='admin123',
    full_name='Admin User'
)
user_service.create_user(admin_user)
print('Admin user created')
"
```

## Environment Configuration Files

### Backend (.env for local development)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/filedb
SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=["http://localhost:3000"]
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100
ENCRYPTION_SECRET=dev-encryption-key-32-characters
```

### Frontend (.env.local for local development)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Briefcase
```

### Frontend (.env.production for Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=Briefcase
```

## SSL and Security

### Railway Backend
- Railway automatically provides HTTPS
- Configure CORS in environment variables
- Set secure JWT secret keys

### Vercel Frontend  
- Vercel automatically provides HTTPS
- Security headers configured in next.config.ts
- CSP headers can be added for additional security

## Monitoring and Logs

### Railway
- Built-in logging in Railway dashboard
- Monitor CPU, memory, and network usage
- Set up alerts for service health

### Vercel
- Built-in analytics and performance monitoring
- Function logs available in dashboard
- Set up Vercel Analytics for user insights

## Scaling Considerations

### Railway Backend
- Auto-scaling available on Pro plans
- Consider database connection pooling for high traffic
- Monitor database performance and upgrade if needed

### Vercel Frontend
- Automatic edge caching and CDN
- Serverless functions scale automatically
- Consider Image Optimization for file previews

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure frontend domain is in ALLOWED_ORIGINS
   - Check that API URL is correct in frontend env

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Ensure database is accessible from Railway

3. **File Upload Issues**
   - Check MAX_FILE_SIZE setting
   - Verify upload directory permissions

4. **Authentication Issues**
   - Ensure SECRET_KEY is set securely
   - Check JWT token expiration settings

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check Vercel deployment logs
vercel logs

# Test API connectivity
curl https://your-backend.railway.app/health

# Test frontend build locally
cd apps/frontend
npm run build
npm run start
```

## Cost Optimization

### Railway
- Use Hobby plan for development ($5/month)
- Pro plan for production ($20/month)
- Monitor resource usage to avoid overages

### Vercel
- Hobby plan includes generous free tier
- Pro plan for team collaboration ($20/month)
- Optimize images and reduce bundle size

## Backup Strategy

### Database Backups
- Railway Pro includes automated backups
- Manual backups: `pg_dump` via Railway CLI
- Store backups in external storage (S3, etc.)

### File Storage Backups
- Implement regular file backup to cloud storage
- Consider using Railway volumes with backup scripts
- Archive old files to reduce storage costs