# Verified Compliance - Ironclad Development Rules & Best Practices

> **CRITICAL**: These rules are non-negotiable. Violations may result in security vulnerabilities, data loss, legal liability, or system failure. All team members must acknowledge and follow these guidelines.

---

## 🚨 ABSOLUTE DESIGN RULES - NO EXCEPTIONS
**CRITICAL REQUIREMENTS - MANDATORY COMPLIANCE**

### Import Rules - ABSOLUTE
- **ONLY single-line imports allowed**
- **NO multi-line imports EVER**
- **NO relative imports EVER**
- **NO from module import (item1, item2) - FORBIDDEN**
- **NO import module.submodule - FORBIDDEN**
- **Example of ONLY allowed format:**
  ```python
  import fastapi
  import sqlalchemy
  import pydantic
  ```

### Testing Rules - ABSOLUTE
- **NO mocks EVER**
- **NO simulations EVER**
- **NO hardcoded responses EVER**
- **NO stubs EVER**
- **NO pass statements EVER**
- **NO fake data EVER**
- **Only real implementations with real data**

**VIOLATION OF THESE RULES = IMMEDIATE REJECTION**

---

## 🔒 TIER 1: ABSOLUTE RULES (NEVER VIOLATE)

### Rule 1.1: GPS & Location Data
**NEVER track location in the background. Period.**

```python
# ❌ FORBIDDEN
def track_location_continuously():
    while True:
        location = get_gps()
        save_to_db(location)
        time.sleep(60)

# ✅ CORRECT
def capture_location_on_demand():
    """Only called during explicit check-in/check-out"""
    if user_action == "check_in" or user_action == "check_out":
        location = get_gps()
        return location
```

### Rule 1.2: Import Rules - ABSOLUTE
**ONLY single-line imports allowed. NO EXCEPTIONS.**

```python
# ❌ FORBIDDEN - Multi-line imports
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, sessionmaker
from typing import List, Optional, Dict

# ❌ FORBIDDEN - Relative imports
from .models import Contact
from ..services import ContactService

# ❌ FORBIDDEN - Submodule imports
import fastapi.applications
import sqlalchemy.orm

# ✅ CORRECT - Single-line imports ONLY
import fastapi
import sqlalchemy
import typing
import uuid
import datetime
import json
import logging
```

### Rule 1.3: Testing Rules - ABSOLUTE
**NO mocks EVER. NO simulations EVER. NO stubs EVER.**

```python
# ❌ FORBIDDEN - Mocks and stubs
from unittest.mock import Mock, patch
def test_with_mock():
    mock_db = Mock()
    mock_service = Mock()

# ❌ FORBIDDEN - Hardcoded responses
def test_api():
    return {"fake": "data"}

# ❌ FORBIDDEN - Pass statements
def test_function():
    pass

# ✅ CORRECT - Real implementations ONLY
def test_contact_creation():
    # REAL database connection
    db = create_test_database()
    service = ContactService(db, real_ghl_client)
    
    # REAL data
    contact_data = ContactCreate(
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )
    
    # REAL implementation
    result = await service.create_contact(contact_data)
    
    # REAL verification
    assert result.email == "test@example.com"
    assert result.id is not None
```

**Enforcement:**
- Code review must verify NO background location services
- Reject any PR adding `background location` permissions
- Location capture ONLY in: `check_in()` and `check_out()` functions
- Code review must verify ONLY single-line imports
- Reject any PR with multi-line or relative imports
- Code review must verify NO mocks, stubs, or simulations
- Reject any PR with fake data or hardcoded responses
- All implementations must be REAL with REAL data
- Flutter: Use `LocationPermission.whileInUse` NEVER `always`
- Log all GPS captures with user action context

**Why:** Privacy laws (GDPR, CCPA), user trust, battery drain, legal liability.

---

### Rule 1.2: Data Encryption & Secrets
**NEVER commit secrets, API keys, or credentials to version control. EVER.**

```bash
# ❌ FORBIDDEN - Hard-coded secrets
DATABASE_URL = "postgresql://user:password123@db.example.com/prod"
GHL_API_KEY = "ghl_sk_abc123xyz789"

# ✅ CORRECT - Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
GHL_API_KEY = os.getenv("GHL_API_KEY")
```

**Enforcement:**
- Use `.env` files (never committed)
- Git hooks to scan for secrets before commit
- Tools: `git-secrets`, `trufflehog`, `detect-secrets`
- All PRs scanned automatically in CI/CD
- Rotate any accidentally exposed secrets immediately (within 1 hour)
- Use GitHub Secrets / Fly.io Secrets for production

**Consequences of violation:** 
- Immediate security incident response
- Force-rotation of all exposed credentials
- Post-mortem required

---

### Rule 1.3: Database Migrations
**NEVER modify the database schema without a migration. NEVER run manual SQL in production.**

```python
# ❌ FORBIDDEN
db.execute("ALTER TABLE sessions ADD COLUMN new_field VARCHAR(255);")

# ✅ CORRECT
# 1. Generate migration
alembic revision --autogenerate -m "Add new_field to sessions"

# 2. Review migration file
# alembic/versions/xxx_add_new_field.py

# 3. Test on staging
alembic upgrade head

# 4. Deploy to production (automated)
```

**Enforcement:**
- All schema changes via Alembic migrations
- Migrations tested on staging before production
- Backup database before running migrations
- NO manual schema changes via pgAdmin/SQL clients
- Migration must be reversible (`downgrade()` function required)

**Why:** Data integrity, version control, rollback capability, team coordination.

---

### Rule 1.4: Personal Data Protection
**NEVER log, display, or transmit PII without explicit need. Treat all user data as confidential.**

```python
# ❌ FORBIDDEN
logger.info(f"User {email} checked in at {lat}, {lng}")
print(f"Contact: {contact.phone}, {contact.email}")

# ✅ CORRECT
logger.info(f"User {contact_id[:8]}... checked in")  # Partial ID only
# Log coordinates separately from identity
logger.info(f"Check-in coordinates: {lat}, {lng}", extra={"contact_id": contact_id})
```

**PII Definition:**
- Email addresses
- Phone numbers
- Full names (given_name + family_name together)
- GPS coordinates (when linked to identity)
- Session notes (may contain personal info)

**Enforcement:**
- Log review: NO PII in application logs
- Sentry: Scrub PII before sending to error tracking
- API responses: Only return PII to authorized users
- Database: Encrypt PII at rest (contact table)
- Analytics: Anonymize data before aggregation

---

### Rule 1.5: Authentication & Authorization
**NEVER trust client-side data. ALWAYS validate ownership server-side.**

```python
# ❌ FORBIDDEN - Trusting client data
@app.patch("/sessions/{session_id}/notes")
def update_notes(session_id: str, notes: str):
    session = db.query(Session).get(session_id)
    session.notes = notes  # No ownership check!
    db.commit()

# ✅ CORRECT - Server-side validation
@app.patch("/sessions/{session_id}/notes")
def update_notes(
    session_id: str, 
    notes: str,
    current_contact = Depends(get_current_contact)
):
    session = db.query(Session).get(session_id)
    
    # Verify ownership
    if session.contact_id != current_contact.id:
        raise HTTPException(403, "Not authorized")
    
    session.notes = notes
    db.commit()
```

**Enforcement:**
- ALL protected endpoints require authentication
- ALL mutations verify resource ownership
- JWT tokens: 15-minute expiration (short-lived)
- NO client-side authorization logic
- Token validation on EVERY request
- Rate limiting: 100 requests/min per IP

**Security Checklist:**
- [ ] Endpoint requires `Depends(get_current_contact)`?
- [ ] Ownership verified: `resource.contact_id == current_contact.id`?
- [ ] Input validated with Pydantic schema?
- [ ] SQL injection prevented (use parameterized queries)?
- [ ] XSS prevented (sanitize user input)?

---

### Rule 1.6: GPS Verification Integrity
**NEVER fake, bypass, or weaken GPS verification. The 200m threshold is sacred.**

```python
# ❌ FORBIDDEN
if distance > 200:
    # "Close enough" logic
    if distance < 500:  # NO!
        location_flag = "ok"

# ❌ FORBIDDEN
if user.is_premium:
    # Skip verification for paid users
    location_flag = "ok"

# ✅ CORRECT
if distance <= 200:
    location_flag = "ok"
else:
    location_flag = "denied"
# No exceptions. No workarounds.
```

**Enforcement:**
- Haversine distance calculation: independently audited
- 200m threshold: hard-coded constant, never configurable
- Location flag: immutable once set
- Log ALL flagged sessions for review
- Alert if flagged sessions exceed 10% of total

**Why:** System integrity, user trust, legal defensibility (even for voluntary tracking).

---

### Rule 1.7: API Backwards Compatibility
**NEVER break existing API contracts. ALWAYS version breaking changes.**

```python
# ❌ FORBIDDEN - Breaking change
# Old: POST /start-session { contact_id, meeting_id }
# New: POST /start-session { user_id, destination_id }  # BREAKS CLIENTS!

# ✅ CORRECT - Versioned endpoint
# Keep: POST /api/v1/sessions/start { contact_id, meeting_id }
# Add:  POST /api/v2/sessions/start { user_id, destination_id }
```

**Versioning Rules:**
- Current version: `/api/v1/*`
- Breaking changes require new version: `/api/v2/*`
- Support old version for minimum 6 months
- Deprecation warnings in response headers
- Mobile apps: graceful degradation for old versions

**Breaking Changes:**
- Removing fields from response
- Changing field types
- Renaming fields
- Changing HTTP status codes
- Adding required request fields

**Non-Breaking Changes (OK):**
- Adding optional fields to request
- Adding new fields to response
- Adding new endpoints
- Bug fixes that don't change behavior

---

## 🛡️ TIER 2: CRITICAL BEST PRACTICES (STRONG RECOMMENDATIONS)

### Rule 2.1: Error Handling & Graceful Degradation

```python
# ❌ BAD
def sync_to_ghl(contact, session):
    ghl_service.webhook(contact, session)  # Crashes if GHL down

# ✅ GOOD
def sync_to_ghl(contact, session):
    try:
        ghl_service.webhook(contact, session)
        logger.info(f"GHL sync success: {session.id}")
    except Exception as e:
        logger.error(f"GHL sync failed: {e}", extra={
            "session_id": session.id,
            "contact_id": contact.id
        })
        # Queue for retry
        retry_queue.add(session.id)
    # Session still completes even if GHL fails
```

**Principles:**
- External service failures NEVER block core functionality
- GHL down? Session still completes, sync retries later
- Geocoding fails? Allow manual lat/lng entry
- Email service down? Log error, retry in background
- GPS timeout? Clear error message with retry option

**Flutter Error Handling:**
```dart
// ❌ BAD
Future<void> checkIn() async {
  final location = await getCurrentLocation(); // Crashes if GPS off
  await apiClient.post('/check-in', {...});
}

// ✅ GOOD
Future<void> checkIn() async {
  try {
    final location = await getCurrentLocation();
    await apiClient.post('/check-in', {...});
    showSuccess("Checked in successfully");
  } on LocationServiceDisabledException {
    showDialog("Location services are disabled. Enable in Settings?");
  } on PermissionDeniedException {
    showDialog("Location permission required. Grant in Settings?");
  } on TimeoutException {
    showDialog("GPS timeout. Move to open area and try again.");
  } on ApiException catch (e) {
    showDialog("Check-in failed: ${e.message}. Retry?");
  }
}
```

---

### Rule 2.2: Database Queries & Performance

**ALWAYS use indexes for query columns. NEVER run N+1 queries.**

```python
# ❌ BAD - N+1 query
sessions = db.query(Session).filter(Session.contact_id == contact_id).all()
for session in sessions:
    check_in = db.query(SessionEvent).filter(
        SessionEvent.session_id == session.id,
        SessionEvent.type == "check_in"
    ).first()  # N queries!

# ✅ GOOD - Single query with join
sessions = db.query(Session).filter(
    Session.contact_id == contact_id
).options(
    joinedload(Session.events)
).all()
```

**Required Indexes:**
```sql
-- Contacts
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_ghl_id ON contacts(ghl_contact_id);

-- Sessions
CREATE INDEX idx_sessions_contact_created ON sessions(contact_id, created_at);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Session Events
CREATE INDEX idx_events_session_type ON session_events(session_id, type);

-- Meetings (Spatial)
CREATE INDEX idx_meetings_location ON meetings USING GIST(
    geography(ST_MakePoint(lng, lat))
);

-- Full-text search
CREATE INDEX idx_sessions_search ON sessions USING GIN(
    to_tsvector('english', dest_name || ' ' || COALESCE(session_notes, ''))
);
```

**Query Performance Rules:**
- Response time target: 95th percentile < 300ms
- Use `EXPLAIN ANALYZE` for slow queries
- Add indexes BEFORE deploying to production
- Monitor slow query log (> 500ms)
- Pagination required for lists (never fetch all)

---

### Rule 2.3: Testing Requirements

**Code without tests is broken code that hasn't been discovered yet.**

**Minimum Test Coverage:**
- Backend: 80% line coverage
- Flutter: 70% line coverage
- Critical paths: 100% coverage

**Required Tests:**

```python
# Backend - MUST have tests for:
def test_check_in_within_threshold():
    """Test check-in succeeds when within 200m"""
    assert location_flag == "ok"

def test_check_in_outside_threshold():
    """Test check-in flagged when > 200m"""
    assert location_flag == "denied"

def test_session_expires_after_15_minutes():
    """Test session expires if no check-in"""
    assert session.status == "expired"

def test_duplicate_contact_rejected():
    """Test duplicate email/phone rejected"""
    with pytest.raises(HTTPException):
        create_contact(email="existing@example.com")

def test_unauthorized_access_blocked():
    """Test user can't access other user's sessions"""
    with pytest.raises(HTTPException) as e:
        update_session(session_id, contact_id=other_user_id)
    assert e.value.status_code == 403
```

```dart
// Flutter - MUST have tests for:
testWidgets('Check-in button disabled until location ready', (tester) async {
  await tester.pumpWidget(SessionScreen());
  
  final button = find.byKey(Key('check_in_button'));
  expect(tester.widget<ElevatedButton>(button).onPressed, isNull);
});

test('Session expires after 15 minutes', () {
  final session = SessionData(expiresAt: DateTime.now().subtract(Duration(minutes: 16)));
  expect(session.isExpired, isTrue);
});

test('Haversine distance calculation accurate', () {
  final distance = calculateDistance(38.5816, -121.4944, 38.5834, -121.4944);
  expect(distance, closeTo(200, 10)); // ~200m ±10m
});
```

**CI/CD Requirements:**
- ALL tests must pass before merge
- PRs without tests = auto-reject
- Coverage must not decrease
- Broken tests block deployment

---

### Rule 2.4: Code Review Standards

**Every PR requires approval from 2 reviewers. No exceptions.**

**Review Checklist:**

```markdown
## Security Review
- [ ] No secrets committed
- [ ] Authentication required on protected endpoints
- [ ] Authorization checks present (ownership verification)
- [ ] Input validation with Pydantic/Dart models
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (no raw HTML rendering)
- [ ] Rate limiting considered

## Data Privacy Review
- [ ] No PII in logs
- [ ] GPS only captured on explicit user action
- [ ] Personal data encrypted at rest
- [ ] Proper consent flows

## Code Quality Review
- [ ] Tests included and passing
- [ ] No N+1 queries
- [ ] Database indexes added if needed
- [ ] Error handling comprehensive
- [ ] Code follows style guide (black, isort for Python)
- [ ] No commented-out code
- [ ] No TODO comments without ticket reference

## Migration Review (if DB changes)
- [ ] Migration reversible (downgrade function works)
- [ ] Tested on staging first
- [ ] Backup plan documented
- [ ] No data loss risk

## API Review (if endpoint changes)
- [ ] Backwards compatible OR versioned
- [ ] OpenAPI docs updated
- [ ] Example requests/responses provided
- [ ] Error codes documented

## Mobile Review (if UI changes)
- [ ] Works on both iOS and Android
- [ ] Handles offline gracefully
- [ ] Loading states present
- [ ] Error messages user-friendly
- [ ] Accessibility considered (screen reader, contrast)
```

**Merge Requirements:**
- ✅ 2 approvals from code owners
- ✅ All CI checks pass
- ✅ No merge conflicts
- ✅ Branch up-to-date with main
- ✅ Tests added for new code
- ✅ Documentation updated

---

### Rule 2.5: Deployment Process

**NEVER deploy directly to production. ALWAYS deploy to staging first.**

**Deployment Stages:**

```
1. Development → Local testing
2. Staging → QA testing (identical to prod)
3. Production → Live users

NEVER skip staging!
```

**Deployment Checklist:**

```markdown
## Pre-Deployment
- [ ] All tests passing on CI
- [ ] Staging deployment successful
- [ ] QA testing completed on staging
- [ ] Performance testing done (load test)
- [ ] Database backup verified
- [ ] Rollback plan documented
- [ ] Migration tested on staging
- [ ] Stakeholders notified

## During Deployment
- [ ] Deploy during low-traffic window
- [ ] Monitor error rates in real-time
- [ ] Monitor API response times
- [ ] Monitor database CPU/memory
- [ ] Check health endpoints
- [ ] Verify GHL integration working

## Post-Deployment
- [ ] Smoke tests passed (critical user flows)
- [ ] Error rates within normal range (< 1%)
- [ ] No spike in 5xx errors
- [ ] Database queries performing well
- [ ] GHL webhooks succeeding
- [ ] Mobile apps connecting successfully

## Rollback Triggers
- Error rate > 5%
- 95th percentile response time > 1000ms
- Database connection failures
- Critical feature broken
- Data corruption detected
```

**Rollback Procedure:**
```bash
# Immediate rollback if issues detected
flyctl deploy --image <previous_image_sha>

# Database rollback if needed
alembic downgrade -1

# Verify rollback successful
curl https://api.myverifiedcompliance.com/health
```

---

### Rule 2.6: Logging & Monitoring

**Log everything important. Log nothing sensitive.**

```python
# ❌ BAD LOGGING
logger.info(f"User check-in: {contact.email} at {lat}, {lng}")

# ✅ GOOD LOGGING
logger.info(
    "Check-in completed",
    extra={
        "event": "check_in",
        "contact_id": str(contact.id)[:8] + "...",  # Partial ID
        "session_id": str(session.id),
        "location_flag": location_flag,
        "accuracy": accuracy,
        "duration_ms": duration_ms
    }
)
```

**Log Levels:**
- **DEBUG**: Development only (verbose)
- **INFO**: Important business events (check-in, check-out, exports)
- **WARNING**: Unexpected but handled (GHL retry, GPS low accuracy)
- **ERROR**: Failures that need attention (webhook failures, API errors)
- **CRITICAL**: System failures (database down, auth system broken)

**Required Logs:**
```python
# User actions
logger.info("contact_created", extra={"contact_id": ...})
logger.info("session_started", extra={"session_id": ..., "source": ...})
logger.info("check_in", extra={"session_id": ..., "location_flag": ...})
logger.info("check_out", extra={"session_id": ..., "duration_min": ...})

# Integration events
logger.info("ghl_webhook_sent", extra={"status": ..., "response_code": ...})
logger.error("ghl_webhook_failed", extra={"error": ..., "retry_count": ...})

# Performance
logger.info("api_request", extra={"endpoint": ..., "duration_ms": ...})

# Security
logger.warning("auth_failed", extra={"ip": ..., "reason": ...})
logger.warning("rate_limit_exceeded", extra={"ip": ..., "endpoint": ...})
```

**Monitoring Alerts:**
```yaml
# Error rate alert
alert: error_rate_high
condition: error_rate > 5% over 5 minutes
severity: critical
action: page on-call, auto-rollback

# Response time alert  
alert: response_time_high
condition: p95_response_time > 1000ms over 10 minutes
severity: warning
action: notify team

# GPS verification alert
alert: location_denial_rate_high
condition: denied_locations > 15% over 1 hour
severity: warning
action: investigate GPS accuracy issues

# GHL integration alert
alert: ghl_webhook_failing
condition: webhook_success_rate < 80% over 30 minutes
severity: high
action: check GHL service status, retry queue
```

---

## 🎯 TIER 3: DEVELOPMENT WORKFLOW (CONSISTENCY & QUALITY)

### Rule 3.1: Git Workflow & Branch Strategy

```
main (production)
  ↑
develop (integration)
  ↑
feature/user-authentication
feature/ghl-integration
hotfix/location-flag-bug
```

**Branch Naming Convention:**
```bash
feature/<ticket-number>-<short-description>
bugfix/<ticket-number>-<short-description>
hotfix/<ticket-number>-<short-description>
release/<version>

# Examples:
feature/VC-123-meeting-search
bugfix/VC-456-gps-timeout
hotfix/VC-789-auth-token-expiry
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>

# Types: feat, fix, docs, style, refactor, test, chore
# Examples:

feat(sessions): add notes editing with 5-min window

- Allow users to edit notes during active session
- Lock notes editing 5 minutes after check-out
- Add timestamp validation

Closes VC-234

---

fix(auth): prevent token expiration during active session

Token was expiring mid-session causing check-out failures.
Extend token TTL to 60 minutes for active sessions.

Fixes VC-567
```

**PR Title Format:**
```
[VC-123] Add meeting search functionality
[VC-456] Fix GPS timeout on Android
[HOTFIX] Critical auth token bug
```

---

### Rule 3.2: Code Style & Formatting

**Python (Backend):**
```bash
# Use black for formatting
black app/ tests/

# Use isort for imports
isort app/ tests/

# Use mypy for type checking
mypy app/

# Configuration in pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
```

**Dart (Flutter):**
```bash
# Use dart format
dart format lib/ test/

# Use dart analyze
dart analyze

# Configuration in analysis_options.yaml
linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - prefer_const_constructors
    - prefer_final_fields
```

**Naming Conventions:**

```python
# Python
class ContactService:  # PascalCase for classes
    def create_contact(self):  # snake_case for functions
        contact_id = uuid.uuid4()  # snake_case for variables
        THRESHOLD_METERS = 200  # UPPER_CASE for constants

# Database
table_name = "contacts"  # snake_case
column_name = "given_name"  # snake_case
```

```dart
// Dart
class ContactProvider {  // PascalCase for classes
  void createContact() {}  // camelCase for methods
  String contactId = '';  // camelCase for variables
  static const int THRESHOLD_METERS = 200;  // UPPER_CASE for constants
}
```

---

### Rule 3.3: Documentation Standards

**Required Documentation:**

```python
# 1. Module docstring
"""
Contact service module.

Handles contact creation, updates, and GHL synchronization.
"""

# 2. Class docstring
class ContactService:
    """
    Service for managing contact operations.
    
    Responsibilities:
    - Create and update contacts
    - Sync with GoHighLevel CRM
    - Validate contact data
    """

# 3. Function docstring
def create_contact(self, contact_data: ContactCreate) -> Contact:
    """
    Create a new contact and sync to GHL.
    
    Args:
        contact_data: Contact information including email, phone, name
        
    Returns:
        Created Contact object with GHL ID populated
        
    Raises:
        HTTPException: If email/phone already exists (409)
        HTTPException: If GHL sync fails (500)
        
    Example:
        >>> service = ContactService(db)
        >>> contact = await service.create_contact(ContactCreate(
        ...     email="user@example.com",
        ...     given_name="John",
        ...     family_name="Doe",
        ...     consent_granted=True
        ... ))
    """
```

**API Documentation (OpenAPI):**
```python
@router.post("/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Create new contact.
    
    - **email**: Valid email address (optional if phone provided)
    - **phone**: E.164 format phone (optional if email provided)
    - **given_name**: First name (required)
    - **family_name**: Last name (required)
    - **consent_granted**: GPS tracking consent (required)
    
    Returns created contact with GHL ID.
    """
```

**README Requirements:**

Every feature folder needs a README:

```markdown
# Feature: Session Management

## Overview
Handles check-in/check-out flow with GPS verification.

## Key Components
- `session_service.py`: Business logic
- `sessions.py`: API endpoints
- `session.py`: Database models

## Flow Diagram
[ASCII diagram or link to diagram]

## Configuration
- `SESSION_EXPIRATION_MINUTES`: Default 15
- `LOCATION_THRESHOLD_METERS`: Default 200

## Testing
```bash
pytest tests/test_sessions.py
```

## Deployment Notes
- Requires PostGIS extension
- Migration: `202501xx_create_sessions_table`
```

---

### Rule 3.4: Environment Management

**Required Environments:**

```
1. Local Development (laptop)
2. Staging (pre-production, identical to prod)
3. Production (live users)
```

**Environment Variables:**

```bash
# .env.development
ENVIRONMENT=development
DATABASE_URL=postgresql://localhost/vc_dev
JWT_SECRET=dev-secret-not-secure
ALLOWED_ORIGINS=["http://localhost:3000"]
DEBUG=true
LOG_LEVEL=DEBUG

# .env.staging
ENVIRONMENT=staging
DATABASE_URL=postgresql://staging-db/vc_staging
JWT_SECRET=<strong-secret>
ALLOWED_ORIGINS=["https://staging.myverifiedcompliance.com"]
DEBUG=false
LOG_LEVEL=INFO

# .env.production
ENVIRONMENT=production
DATABASE_URL=<encrypted>
JWT_SECRET=<encrypted-strong-secret>
ALLOWED_ORIGINS=["https://myverifiedcompliance.com"]
DEBUG=false
LOG_LEVEL=WARNING
SENTRY_DSN=<sentry-url>
```

**Secret Rotation Schedule:**
- JWT secrets: Every 90 days
- HMAC secrets: Every 90 days
- API keys: Every 180 days
- Database passwords: Every 180 days

---

## 🚨 INCIDENT RESPONSE PROCEDURES

### Critical Incident Classification

**P0 - Critical (Respond immediately)**
- System completely down
- Data breach or exposure
- Payment system failure (if applicable)
- Mass user impact (>50% users affected)

**P1 - High (Respond within 1 hour)**
- Core feature broken (check-in/out failing)
- GHL integration down
- Database performance severely degraded
- Security vulnerability discovered

**P2 - Medium (Respond within 4 hours)**
- Non-critical feature broken
- Performance degradation (<50% users affected)
- Third-party service degraded

**P3 - Low (Respond within 24 hours)**
- Minor bugs
- UI issues
- Documentation errors

### Incident Response Process

```markdown
## 1. DETECT (Automated monitoring alerts)
- Sentry errors spike
- Uptime monitor reports downtime
- User reports via support

## 2. TRIAGE (Within 5 minutes)
- Assign severity (P0-P3)
- Notify on-call engineer
- Create incident ticket

## 3. INVESTIGATE (Immediately for P0/P1)
- Check logs in Logtail/Sentry
- Review recent deployments
- Check external service status (GHL, Google Maps)
- Identify root cause

## 4. MITIGATE (As quickly as possible)
- Rollback deployment if recent
- Apply hotfix if quick
- Scale resources if performance issue
- Disable feature if necessary

## 5. RESOLVE (Verify fix)
- Deploy fix to production
- Verify metrics return to normal
- Test affected flows
- Monitor for 30 minutes

## 6. COMMUNICATE (Throughout process)
- Update status page
- Notify affected users
- Post in team Slack
- Log all actions in incident ticket

## 7. POST-MORTEM (Within 48 hours for P0/P1)
- Timeline of events
- Root cause analysis
- Action items to prevent recurrence
- Share learnings with team
```

---

## 📋 DEFINITION OF DONE

**Feature is NOT done until:**

- [ ] Code complete and follows style guide
- [ ] Unit tests written (80% coverage)
- [ ] Integration tests written (if applicable)
- [ ] Code reviewed and approved by 2 engineers
- [ ] Documentation updated (README, API docs)
- [ ] Tested on staging environment
- [ ] QA testing completed
- [ ] Security review passed
- [ ] Performance tested (no regression)
- [ ] Database migrations tested
- [ ] Backwards compatibility verified
- [ ] Error handling comprehensive
- [ ] Logging added for key events
- [ ] Monitoring/alerts configured
- [ ] Deployed to production
- [ ] Post-deployment smoke tests passed
- [ ] Stakeholders notified
- [ ] Ticket closed and demo recorded

---

## 🎓 ONBOARDING CHECKLIST (New Developers)

**Day 1: Setup**
- [ ] GitHub access granted
- [ ] Development environment setup complete
- [ ] Run app locally (backend + frontend)
- [ ] Read this document (Ironclad Rules)
- [ ] Acknowledge understanding of security requirements

**Week 1: Learning**
- [ ] Complete one small bug fix
- [ ] Shadow code review process
- [ ] Review system architecture diagram
- [ ] Read GHL integration documentation
- [ ] Understand GPS verification logic

**Week 2: Contributing**
- [ ] Complete first feature (with mentor)
- [ ] Write tests for feature
- [ ] Submit PR for review
- [ ] Deploy to staging

**Week 3: Independence**
- [ ] Complete feature independently
- [ ] Participate in code reviews
- [ ] Understand deployment process
- [ ] On-call rotation readiness

---

## 📞 SUPPORT & ESCALATION

**Technical Issues:**
1. Check documentation
2. Ask in team Slack (#dev-help)
3. Create GitHub issue
4. Escalate to tech lead

**Security Issues:**
1. Report immediately to security lead
2. Do NOT discuss publicly
3. Follow security incident process
4. Document in private channel

**Production Incidents:**
1. Follow incident response process
2. Page on-call engineer
3. Update status page
4. Notify stakeholders

---

## ✅ ACKNOWLEDGMENT

**I have read and understand these rules. I commit to:**
- Following all Tier 1 rules without exception
- Adhering to Tier 2 best practices
- Maintaining code quality standards
- Prioritizing security and privacy
- Reporting violations when observed

**Signature:** _________________  
**Date:** _________________  
**Team:** _________________

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Review Frequency:** Quarterly