# Deploying Briefcase Backend to Railway

This guide explains how to deploy the Briefcase backend application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional): Install from [docs.railway.app/develop/cli](https://docs.railway.app/develop/cli)
3. **GitHub Repository**: Push your code to GitHub for automatic deployments

## Deployment Steps

### 1. Create New Project

1. Log into Railway Dashboard
2. Click "New Project"
3. Choose "Deploy from GitHub repo" and select your repository
4. Railway will automatically detect the configuration

### 2. Add PostgreSQL Database

1. In your project, click "New Service"
2. Select "Database" > "PostgreSQL"
3. Railway will automatically inject the `DATABASE_URL` environment variable

### 3. Configure Environment Variables

1. Click on your backend service
2. Go to "Variables" tab
3. Add the following required variables:

```bash
# Security (REQUIRED - Generate strong random values)
SECRET_KEY=<generate using: openssl rand -hex 32>
MASTER_KEY=<generate using: openssl rand -hex 32>

# CORS (REQUIRED - Add your frontend domain)
CORS_ORIGINS=https://your-frontend-domain.com

# Optional but recommended
ENVIRONMENT=production
LOG_LEVEL=info
```

See `.env.railway.example` for all available variables.

### 4. Deploy

Railway will automatically:
1. Build your application using the Dockerfile
2. Run database migrations
3. Start the web service
4. Set up cron jobs for lifecycle management

## Configuration Files

Railway supports multiple configuration formats:

- **railway.yaml**: Full multi-service configuration with cron jobs (recommended)
- **railway.json**: Simple single-service configuration
- **Dockerfile**: Container-based deployment

## Cron Jobs

The following automated jobs are configured:

| Job | Schedule | Purpose |
|-----|----------|---------|
| expire-documents | Every 30 minutes | Mark expired documents |
| cleanup-documents | Daily at 2 AM UTC | Remove deleted documents |
| cleanup-audit-logs | Weekly Sunday 3 AM | Clean old audit logs |

## Monitoring

### Health Check
- Endpoint: `/health`
- Checks database connectivity and service status

### Logs
- View in Railway Dashboard > Service > Logs
- Or use Railway CLI: `railway logs`

### Metrics
- Available at `/api/v1/admin/metrics` (requires admin auth)
- System overview at `/api/v1/admin/system-overview`

## Custom Domain

1. Go to Service Settings > Networking
2. Add your custom domain
3. Configure DNS with provided CNAME record
4. Enable HTTPS (automatic with Railway)

## Scaling

### Horizontal Scaling
Edit `railway.yaml`:
```yaml
deploy:
  numReplicas: 3  # Increase for more instances
```

### Vertical Scaling
Upgrade your Railway plan for more resources

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL service is running
- Check DATABASE_URL is properly set
- Verify migrations have run: `railway run alembic upgrade head`

### Authentication Errors
- Verify SECRET_KEY is set and consistent
- Check CORS_ORIGINS includes your frontend domain
- Ensure MASTER_KEY is set for encryption

### Cron Jobs Not Running
- Check cron syntax in railway.yaml
- Verify scripts exist in app/scripts/
- Check logs for specific cron services

### Build Failures
- Ensure pyproject.toml is valid
- Check Dockerfile syntax
- Verify all dependencies are installable

## Security Checklist

- [ ] Strong SECRET_KEY generated (32+ characters)
- [ ] Strong MASTER_KEY generated (32+ characters)
- [ ] CORS_ORIGINS restricted to your domains only
- [ ] Database is not publicly accessible
- [ ] HTTPS enabled on custom domain
- [ ] Rate limiting configured
- [ ] Environment set to "production"
- [ ] Debug mode disabled

## Commands

### Railway CLI Commands
```bash
# Login
railway login

# Link to project
railway link

# Deploy manually
railway up

# View logs
railway logs

# Run commands in production
railway run python app/scripts/expire_documents.py

# Open dashboard
railway open
```

### Database Management
```bash
# Run migrations
railway run alembic upgrade head

# Create new migration
railway run alembic revision --autogenerate -m "description"

# Rollback migration
railway run alembic downgrade -1
```

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Application Issues: Check logs and health endpoint first