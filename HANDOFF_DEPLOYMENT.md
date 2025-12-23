# Verified Compliance™ — Deployment Guide

## Production Deployment & Infrastructure

---

## Current Infrastructure

### Production Environment

| Component | Service | Region |
|-----------|---------|--------|
| Backend API | Fly.io | US (auto-scale) |
| Database | Neon PostgreSQL | US-East |
| File Storage | (To be configured) | - |
| CDN | (To be configured) | - |
| Monitoring | Sentry | Cloud |

### URLs

| Environment | Backend URL | Frontend URL |
|-------------|-------------|--------------|
| Production | `https://api.verifiedcompliance.com` | `https://app.verifiedcompliance.com` |
| Staging | `https://api-staging.verifiedcompliance.com` | `https://staging.verifiedcompliance.com` |
| Local Dev | `http://localhost:8000` | `http://localhost:3000` |

---

## Backend Deployment (Fly.io)

### Prerequisites

1. Install Fly CLI:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. Authenticate:
   ```bash
   fly auth login
   ```

### Configuration Files

**fly.toml** (in backend/):
```toml
app = "verified-compliance-api"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile.prod"

[env]
  PORT = "8080"
  
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  
  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

**Dockerfile.prod**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start command
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
```

### Deployment Commands

```bash
cd backend

# First deployment
fly launch

# Subsequent deployments
fly deploy

# View logs
fly logs

# SSH into container
fly ssh console

# Scale up
fly scale count 2

# View status
fly status
```

### Environment Secrets

```bash
# Set production secrets
fly secrets set DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
fly secrets set SECRET_KEY="your-production-secret-key"
fly secrets set GHL_API_KEY="your-ghl-api-key"
fly secrets set GHL_LOCATION_ID="your-location-id"
fly secrets set GOOGLE_MAPS_API_KEY="your-maps-key"
fly secrets set SENTRY_DSN="your-sentry-dsn"

# List secrets
fly secrets list

# Remove secret
fly secrets unset SECRET_NAME
```

---

## Database Deployment (Neon)

### Setup

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string

### Connection String Format

```
postgresql+asyncpg://user:password@ep-xxx-yyy.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### Migrations in Production

```bash
# SSH into Fly container
fly ssh console

# Run migrations
alembic upgrade head

# Check current version
alembic current
```

### Backup Strategy

Neon provides:
- Point-in-time recovery (7 days free tier)
- Branch creation for testing
- Automatic daily backups

---

## Frontend Deployment

### Flutter Web Build

```bash
cd frontend

# Build for web
flutter build web --release

# Output in build/web/
```

### Deployment Options

**Option A: Fly.io Static Site**

Create `Dockerfile` in frontend/:
```dockerfile
FROM nginx:alpine
COPY build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Option B: Vercel/Netlify**

1. Connect GitHub repository
2. Configure build command: `flutter build web`
3. Set output directory: `build/web`

**Option C: Firebase Hosting**

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy
```

### Mobile App Distribution

**Android (Google Play)**
```bash
# Build release APK
flutter build apk --release

# Build App Bundle (recommended)
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab
```

**iOS (App Store)**
```bash
# Build iOS
flutter build ios --release

# Open in Xcode for archive
open ios/Runner.xcworkspace
# Product → Archive → Distribute App
```

---

## CI/CD Pipeline (GitHub Actions)

### Backend Workflow

**.github/workflows/backend.yml**:
```yaml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths: ['backend/**']
  pull_request:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
        run: |
          poetry run pytest --cov=app
      
      - name: Terminology check
        working-directory: ./backend
        run: |
          python scripts/terminology_check.py --dir app

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - name: Deploy to Fly.io
        working-directory: ./backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: flyctl deploy --remote-only
```

### Frontend Workflow

**.github/workflows/frontend.yml**:
```yaml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths: ['frontend/**']
  pull_request:
    branches: [main]
    paths: ['frontend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Install dependencies
        working-directory: ./frontend
        run: flutter pub get
      
      - name: Analyze
        working-directory: ./frontend
        run: flutter analyze
      
      - name: Test
        working-directory: ./frontend
        run: flutter test

  build-web:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Build web
        working-directory: ./frontend
        run: |
          flutter pub get
          flutter build web --release
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: web-build
          path: frontend/build/web
```

---

## Monitoring & Logging

### Sentry Setup

**Backend (Python)**:
```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
)
```

**Frontend (Flutter)**:
```dart
// main.dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = 'your-sentry-dsn';
      options.environment = 'production';
    },
    appRunner: () => runApp(MyApp()),
  );
}
```

### Health Check Endpoint

```python
# app/api/v1/endpoints/health.py
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )
```

### Uptime Monitoring

Configure UptimeRobot or similar:
- Monitor: `https://api.verifiedcompliance.com/health`
- Interval: 5 minutes
- Alert on: 2 consecutive failures

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://...` |
| `SECRET_KEY` | JWT signing key | 64-char random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `GHL_API_KEY` | GoHighLevel API key | `ghl_...` |
| `GHL_LOCATION_ID` | GHL location | `loc_...` |
| `GOOGLE_MAPS_API_KEY` | Maps API key | `AIza...` |
| `SENTRY_DSN` | Sentry project DSN | `https://...@sentry.io/...` |
| `CORS_ORIGINS` | Allowed origins | `https://app.verifiedcompliance.com` |
| `ENVIRONMENT` | Environment name | `production` |

### Generating Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

---

## Rollback Procedures

### Backend Rollback

```bash
# List recent deployments
fly releases

# Rollback to previous release
fly deploy --image registry.fly.io/verified-compliance-api:v42

# Or use release number
fly releases rollback 42
```

### Database Rollback

```bash
# SSH into container
fly ssh console

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### Emergency Procedures

1. **High Error Rate**
   - Check Sentry for errors
   - Review recent deployments
   - Rollback if necessary

2. **Database Issues**
   - Check Neon dashboard
   - Verify connection string
   - Check for locked queries

3. **Complete Outage**
   - Check Fly.io status page
   - Check Neon status page
   - Contact support if infrastructure issue

---

## Security Checklist

### Before Going Live

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS properly (not `*`)
- [ ] Enable HTTPS only
- [ ] Set up Sentry for error tracking
- [ ] Configure rate limiting
- [ ] Test authentication flows
- [ ] Review all environment variables
- [ ] Set up database backups
- [ ] Test rollback procedures

### Regular Maintenance

- [ ] Weekly: Review error logs
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review access logs
- [ ] Quarterly: Security audit
- [ ] Quarterly: Backup restore test

---

## Cost Estimates

### Monthly Costs (Approximate)

| Service | Plan | Cost |
|---------|------|------|
| Fly.io | 2 VMs, 512MB | ~$10-20 |
| Neon PostgreSQL | Free tier | $0 |
| Sentry | Free tier | $0 |
| Domain | Annual | ~$15/year |
| **Total** | | **~$15-25/month** |

### Scaling Costs

- Additional Fly.io VMs: ~$5/month each
- Neon paid plans: Starting at $19/month
- Higher Sentry volume: Starting at $26/month

---

**For deployment issues, check Fly.io documentation or Sentry error reports.**

