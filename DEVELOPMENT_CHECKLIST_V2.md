# Verified Compliance™ — Granular Development Checklist v2.0

## Purpose
This document provides **extremely detailed, step-by-step implementation guidance** for developers. Each checklist item is atomic and can be completed independently.

---

# PHASE 1: FOUNDATION (Weeks 1-4)

## Week 1: Terminology Enforcement & Disclaimers

### Day 1-2: CI/CD Terminology Linting

#### Backend Terminology Scanner

```
FILE: backend/scripts/terminology_check.py
```

- [ ] Create new file `backend/scripts/terminology_check.py`
- [ ] Add shebang line: `#!/usr/bin/env python3`
- [ ] Add imports:
  ```python
  import sys
  import re
  import pathlib
  import argparse
  ```
- [ ] Define `PROHIBITED_TERMS` constant:
  ```python
  PROHIBITED_TERMS = [
      r'\bverified\b',      # except in file names, imports
      r'\bproven\b',
      r'\bconfirmed\b',
      r'\bcompliance\s+score\b',
      r'\bpass/fail\b',
      r'\bpass\s*/\s*fail\b',
  ]
  ```
- [ ] Define `ALLOWED_PATTERNS` constant:
  ```python
  ALLOWED_PATTERNS = [
      r'verified_at',
      r'email_verified',
      r'phone_verified',
      r'verification_',
      r'VerificationProvider',
      r'verification_proof',
  ]
  ```
- [ ] Implement `is_allowed_context(line: str, term: str) -> bool` function
- [ ] Implement `scan_file(filepath: pathlib.Path) -> list[tuple[int, str, str]]` function
  - Return list of (line_number, line_content, matched_term)
- [ ] Implement `scan_directory(directory: pathlib.Path, extensions: list[str]) -> dict` function
- [ ] Implement `main()` function with argparse
- [ ] Add `if __name__ == "__main__"` block
- [ ] Test locally with: `python scripts/terminology_check.py --dir app --ext .py`
- [ ] Verify exit code 0 for clean, 1 for violations

#### GitHub Actions Integration

```
FILE: .github/workflows/ci.yml
```

- [ ] Open existing `.github/workflows/ci.yml`
- [ ] Add new job `terminology-check` after `lint` job:
  ```yaml
  terminology-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Check Backend Terminology
        run: python backend/scripts/terminology_check.py --dir backend/app --ext .py
      - name: Check Frontend Terminology
        run: python backend/scripts/terminology_check.py --dir frontend/lib --ext .dart
  ```
- [ ] Add job dependency: `needs: [lint, terminology-check]` to test job
- [ ] Commit and push to feature branch
- [ ] Verify CI runs terminology check
- [ ] Verify CI fails on prohibited term (test with intentional violation)
- [ ] Remove test violation and verify CI passes

#### Pre-commit Hook

```
FILE: .pre-commit-config.yaml
```

- [ ] Create or update `.pre-commit-config.yaml`:
  ```yaml
  repos:
    - repo: local
      hooks:
        - id: terminology-check
          name: Terminology Check
          entry: python backend/scripts/terminology_check.py --files
          language: python
          types: [python, dart]
          pass_filenames: true
  ```
- [ ] Update `--files` argument handling in terminology_check.py
- [ ] Test locally: `pre-commit run terminology-check --all-files`
- [ ] Document in `CONTRIBUTING.md`

### Day 3-4: Disclaimer Banner Widget

#### Backend Response Schema

```
FILE: backend/app/schemas/common.py
```

- [ ] Create new file `backend/app/schemas/common.py`
- [ ] Add imports:
  ```python
  from pydantic import BaseModel
  from typing import Optional
  ```
- [ ] Define `STANDARD_DISCLAIMER` constant:
  ```python
  STANDARD_DISCLAIMER = (
      "This is a documentation record. Final determinations are "
      "made by your supervising professional."
  )
  ```
- [ ] Create `DisclaimerMixin` class:
  ```python
  class DisclaimerMixin(BaseModel):
      disclaimer_text: str = STANDARD_DISCLAIMER
      is_documentation_record: bool = True
  ```
- [ ] Export in `backend/app/schemas/__init__.py`

```
FILE: backend/app/schemas/session.py
```

- [ ] Import `DisclaimerMixin` from common
- [ ] Update `SessionResponse` to inherit from `DisclaimerMixin`:
  ```python
  class SessionResponse(DisclaimerMixin):
      # existing fields...
  ```
- [ ] Update `SessionDetails` similarly
- [ ] Run tests: `pytest tests/test_schemas.py -v`
- [ ] Verify API response includes disclaimer fields

#### Frontend Banner Widget

```
FILE: frontend/lib/ui/widgets/vc_disclaimer_banner.dart
```

- [ ] Create new file `frontend/lib/ui/widgets/vc_disclaimer_banner.dart`
- [ ] Add imports:
  ```dart
  import 'package:flutter/material.dart';
  ```
- [ ] Define `VCDisclaimerBanner` StatelessWidget:
  ```dart
  class VCDisclaimerBanner extends StatelessWidget {
    final String? customText;
    
    const VCDisclaimerBanner({
      super.key,
      this.customText,
    });
    
    static const String defaultText = 
        'This is a documentation record. Final determinations are '
        'made by your supervising professional.';
    
    @override
    Widget build(BuildContext context) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.amber.shade100,
          border: Border(
            bottom: BorderSide(color: Colors.amber.shade400, width: 1),
          ),
        ),
        child: Row(
          children: [
            Icon(
              Icons.info_outline,
              color: Colors.amber.shade900,
              size: 20,
              semanticLabel: 'Information',
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Semantics(
                label: 'Disclaimer',
                child: Text(
                  customText ?? defaultText,
                  style: TextStyle(
                    color: Colors.amber.shade900,
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ),
            ),
          ],
        ),
      );
    }
  }
  ```
- [ ] Export in `frontend/lib/ui/widgets/widgets.dart`:
  ```dart
  export 'vc_disclaimer_banner.dart';
  ```

#### Integrate Banner Into Screens

```
FILE: frontend/lib/features/sessions/screens/session_screen.dart
```

- [ ] Import banner widget
- [ ] Add banner below AppBar, before content:
  ```dart
  body: Column(
    children: [
      const VCDisclaimerBanner(),
      Expanded(
        child: // existing content
      ),
    ],
  ),
  ```
- [ ] Repeat for `session_list_screen.dart`
- [ ] Repeat for reports screen
- [ ] Hot reload and verify banner displays

#### Widget Tests

```
FILE: frontend/test/widgets/vc_disclaimer_banner_test.dart
```

- [ ] Create test file
- [ ] Add imports:
  ```dart
  import 'package:flutter_test/flutter_test.dart';
  import 'package:flutter/material.dart';
  import 'package:verified_compliance/ui/widgets/vc_disclaimer_banner.dart';
  ```
- [ ] Write test: `renders default text`:
  ```dart
  testWidgets('renders default text', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: VCDisclaimerBanner())),
    );
    expect(find.text(VCDisclaimerBanner.defaultText), findsOneWidget);
  });
  ```
- [ ] Write test: `renders custom text when provided`
- [ ] Write test: `has correct semantic label for accessibility`
- [ ] Write test: `displays info icon`
- [ ] Run tests: `flutter test test/widgets/vc_disclaimer_banner_test.dart`

---

## Week 2: Review Artifacts & Immutability

### Day 1-2: Review Artifact Database Model

#### Create Model File

```
FILE: backend/app/models/review_artifact.py
```

- [ ] Create new file
- [ ] Add docstring: `"""ReviewArtifact model for storing immutable professional decisions"""`
- [ ] Add imports:
  ```python
  import uuid
  import enum
  from datetime import datetime
  from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
  from sqlalchemy.orm import relationship
  from app.models.base import Base
  ```
- [ ] Define `ReviewDecisionType` enum:
  ```python
  class ReviewDecisionType(enum.Enum):
      APPROVED = "approved"
      REJECTED = "rejected"
      FLAGGED = "flagged"
      ANNOTATED = "annotated"
  ```
- [ ] Define `ReviewArtifact` class:
  ```python
  class ReviewArtifact(Base):
      __tablename__ = "review_artifacts"
      
      id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
      source_record_id = Column(String(36), nullable=False, index=True)
      source_record_type = Column(String(50), nullable=False)
      decision_type = Column(Enum(ReviewDecisionType), nullable=False)
      reviewer_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
      reviewer_credential_state = Column(String(50), nullable=True)
      reason = Column(Text, nullable=True)
      annotation = Column(Text, nullable=True)
      policy_version_id = Column(String(36), nullable=True)
      created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
  ```
- [ ] Add `__repr__` method
- [ ] Add `__init__` method with UUID generation

#### Update Models __init__.py

```
FILE: backend/app/models/__init__.py
```

- [ ] Add import: `from app.models.review_artifact import ReviewArtifact, ReviewDecisionType`
- [ ] Add to `__all__` list: `"ReviewArtifact"`, `"ReviewDecisionType"`

#### Create Alembic Migration

```
COMMAND: cd backend && alembic revision -m "add_review_artifacts"
```

- [ ] Run alembic revision command
- [ ] Open generated migration file
- [ ] Implement `upgrade()`:
  ```python
  def upgrade():
      op.create_table(
          'review_artifacts',
          sa.Column('id', sa.String(36), primary_key=True),
          sa.Column('source_record_id', sa.String(36), nullable=False, index=True),
          sa.Column('source_record_type', sa.String(50), nullable=False),
          sa.Column('decision_type', sa.Enum('approved', 'rejected', 'flagged', 'annotated', name='reviewdecisiontype'), nullable=False),
          sa.Column('reviewer_id', sa.String(36), sa.ForeignKey('contacts.id'), nullable=False),
          sa.Column('reviewer_credential_state', sa.String(50), nullable=True),
          sa.Column('reason', sa.Text, nullable=True),
          sa.Column('annotation', sa.Text, nullable=True),
          sa.Column('policy_version_id', sa.String(36), nullable=True),
          sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
      )
      op.create_index('ix_review_artifacts_reviewer_id', 'review_artifacts', ['reviewer_id'])
      op.create_index('ix_review_artifacts_created_at', 'review_artifacts', ['created_at'])
  ```
- [ ] Implement `downgrade()`:
  ```python
  def downgrade():
      op.drop_table('review_artifacts')
      op.execute("DROP TYPE IF EXISTS reviewdecisiontype")
  ```
- [ ] Test migration: `alembic upgrade head`
- [ ] Test downgrade: `alembic downgrade -1`
- [ ] Re-apply: `alembic upgrade head`

#### Add Immutability Trigger (PostgreSQL)

```
FILE: backend/alembic/versions/XXX_add_review_artifact_immutability.py
```

- [ ] Create new migration for trigger
- [ ] Implement `upgrade()`:
  ```python
  def upgrade():
      op.execute("""
          CREATE OR REPLACE FUNCTION prevent_review_artifact_update()
          RETURNS TRIGGER AS $$
          BEGIN
              RAISE EXCEPTION 'Review artifacts are immutable and cannot be updated';
          END;
          $$ LANGUAGE plpgsql;
          
          CREATE TRIGGER review_artifact_immutable
          BEFORE UPDATE ON review_artifacts
          FOR EACH ROW
          EXECUTE FUNCTION prevent_review_artifact_update();
      """)
  ```
- [ ] Implement `downgrade()`:
  ```python
  def downgrade():
      op.execute("DROP TRIGGER IF EXISTS review_artifact_immutable ON review_artifacts")
      op.execute("DROP FUNCTION IF EXISTS prevent_review_artifact_update")
  ```
- [ ] Run migration

### Day 3-4: Review Service & API

#### Create Schema

```
FILE: backend/app/schemas/review.py
```

- [ ] Create new file
- [ ] Add imports
- [ ] Create `ReviewArtifactCreate` schema:
  ```python
  class ReviewArtifactCreate(BaseModel):
      source_record_id: str
      source_record_type: str
      decision_type: ReviewDecisionType
      reason: Optional[str] = None
      annotation: Optional[str] = None
      
      @validator('reason')
      def reason_required_for_rejection(cls, v, values):
          if values.get('decision_type') == ReviewDecisionType.REJECTED and not v:
              raise ValueError('Reason is required when rejecting a record')
          return v
  ```
- [ ] Create `ReviewArtifactResponse` schema:
  ```python
  class ReviewArtifactResponse(BaseModel):
      id: str
      source_record_id: str
      source_record_type: str
      decision_type: ReviewDecisionType
      reviewer_id: str
      reviewer_credential_state: Optional[str]
      reason: Optional[str]
      annotation: Optional[str]
      created_at: datetime
      
      class Config:
          from_attributes = True
  ```

#### Create Service

```
FILE: backend/app/services/review_service.py
```

- [ ] Create new file
- [ ] Add docstring
- [ ] Add imports
- [ ] Create `ReviewService` class:
  ```python
  class ReviewService:
      async def create_review_artifact(
          self,
          data: ReviewArtifactCreate,
          reviewer_id: str,
          reviewer_credential_state: str,
          db: AsyncSession
      ) -> ReviewArtifact:
          artifact = ReviewArtifact(
              source_record_id=data.source_record_id,
              source_record_type=data.source_record_type,
              decision_type=data.decision_type,
              reviewer_id=reviewer_id,
              reviewer_credential_state=reviewer_credential_state,
              reason=data.reason,
              annotation=data.annotation,
          )
          db.add(artifact)
          await db.commit()
          await db.refresh(artifact)
          return artifact
  ```
- [ ] Implement `get_artifacts_for_record(record_id, db)` method
- [ ] Implement `export_artifacts(contact_id, date_range, db)` method
- [ ] Add logging throughout

#### Create API Endpoint

```
FILE: backend/app/api/v1/endpoints/reviews.py
```

- [ ] Create new file
- [ ] Add imports
- [ ] Create router: `router = APIRouter(prefix="/reviews", tags=["reviews"])`
- [ ] Implement `POST /` endpoint:
  ```python
  @router.post("/", response_model=ReviewArtifactResponse, status_code=201)
  async def create_review(
      data: ReviewArtifactCreate,
      current_user: Contact = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      # Verify user is a professional
      # Get credential state
      # Call service
      pass
  ```
- [ ] Implement `GET /{record_id}` endpoint
- [ ] Implement `GET /export` endpoint
- [ ] Register router in `backend/app/api/v1/router.py`

#### Write Tests

```
FILE: backend/tests/test_review_service.py
```

- [ ] Create test file
- [ ] Write test: `test_create_review_artifact_success`
- [ ] Write test: `test_create_rejection_requires_reason`
- [ ] Write test: `test_artifacts_are_immutable`
- [ ] Write test: `test_get_artifacts_for_record`
- [ ] Run tests: `pytest tests/test_review_service.py -v`

---

## Week 3: 2FA & Verification System

### Day 1-2: Database Models for 2FA

#### Extend Contact Model

```
FILE: backend/app/models/contact.py
```

- [ ] Add new columns after existing columns:
  ```python
  # 2FA Fields
  phone_verified = Column(Boolean, default=False, nullable=False)
  phone_verified_at = Column(DateTime(timezone=True), nullable=True)
  email_verified = Column(Boolean, default=False, nullable=False)
  email_verified_at = Column(DateTime(timezone=True), nullable=True)
  twofa_enabled = Column(Boolean, default=False, nullable=False)
  twofa_setup_completed_at = Column(DateTime(timezone=True), nullable=True)
  totp_secret_encrypted = Column(String(255), nullable=True)
  ```
- [ ] Add property:
  ```python
  @property
  def is_2fa_complete(self) -> bool:
      return self.phone_verified and self.email_verified and self.twofa_enabled
  ```

#### Create VerificationCode Model

```
FILE: backend/app/models/verification_code.py
```

- [ ] Create new file with full model
- [ ] Define `VerificationCodeType` enum: `PHONE`, `EMAIL`, `TOTP_SETUP`
- [ ] Define `VerificationCode` class with columns:
  - `id`, `contact_id`, `code_type`, `code_hash`, `expires_at`, `used_at`, `attempts`, `max_attempts`
- [ ] Add methods:
  - `is_valid() -> bool`
  - `mark_used()`
  - `increment_attempts()`

#### Create Migration

- [ ] Run: `alembic revision -m "add_2fa_fields"`
- [ ] Implement upgrade with new columns and table
- [ ] Test migration

### Day 3-4: Verification Service

#### Create VerificationService

```
FILE: backend/app/services/verification_service.py
```

- [ ] Create new file
- [ ] Implement `generate_code() -> str` (6-digit random)
- [ ] Implement `hash_code(code: str) -> str` using bcrypt
- [ ] Implement `send_phone_verification(contact_id, db)`:
  - Generate code
  - Hash and store
  - Send via SMS service
  - Return success/failure
- [ ] Implement `verify_phone_code(contact_id, code, db)`:
  - Get latest code
  - Check attempts
  - Verify hash
  - Mark used
  - Update contact
- [ ] Implement similar for email
- [ ] Implement TOTP setup:
  - Generate secret
  - Generate QR code data
  - Store encrypted secret
- [ ] Implement TOTP verification

#### Create SMS Service

```
FILE: backend/app/services/sms_service.py
```

- [ ] Create new file
- [ ] Add Twilio client setup
- [ ] Implement `send_sms(to: str, body: str) -> bool`
- [ ] Add error handling and logging
- [ ] Create mock mode for development

### Day 5: API Endpoints

```
FILE: backend/app/api/v1/endpoints/verification.py
```

- [ ] Create all verification endpoints
- [ ] Add rate limiting
- [ ] Add tests

---

## Week 4: Consent Artifacts & Identity

### Day 1-2: Consent System

#### ConsentArtifact Model

```
FILE: backend/app/models/consent_artifact.py
```

- [ ] Create model with all fields
- [ ] Create migration
- [ ] Add immutability trigger

#### ConsentService

```
FILE: backend/app/services/consent_service.py
```

- [ ] Implement `record_consent()`
- [ ] Implement `get_consents()`
- [ ] Implement `has_all_required_consents()`
- [ ] Implement `export_consents()`

### Day 3-4: Identity System

#### UserIdentity Model

- [ ] Create model
- [ ] Create Jurisdiction model
- [ ] Create migrations
- [ ] Seed initial jurisdictions

### Day 5: Integration

- [ ] Update registration flow to collect identity
- [ ] Update registration flow to require consents
- [ ] Write integration tests

---

# PHASE 2: MANDATE & ENROLLMENT (Weeks 5-8)

## Week 5: Mandate Models

### Mandate Model

```
FILE: backend/app/models/mandate.py
```

Complete checklist:
- [ ] Create file with docstring
- [ ] Import dependencies
- [ ] Define `MandateStatus` enum
- [ ] Define `Mandate` class with all columns
- [ ] Add relationships
- [ ] Create migration
- [ ] Write model tests

### EnrollmentToken Model

```
FILE: backend/app/models/enrollment_token.py
```

- [ ] Create complete model
- [ ] Add secure token generation
- [ ] Add expiration logic
- [ ] Create migration

## Week 6: Mandate Service & API

### MandateService

```
FILE: backend/app/services/mandate_service.py
```

- [ ] Implement `create_mandate()`
- [ ] Implement `generate_enrollment_token()`
- [ ] Implement `send_enrollment_sms()`
- [ ] Implement `validate_token()`
- [ ] Implement `complete_enrollment()`
- [ ] Write comprehensive tests

### API Endpoints

- [ ] Create all mandate endpoints
- [ ] Add authentication middleware
- [ ] Add authorization checks (professional only)

## Week 7-8: Frontend Enrollment

### Deep Link Handler

- [ ] Configure URL scheme
- [ ] Handle enrollment URLs
- [ ] Navigate to enrollment flow

### Enrollment Screens

- [ ] `EnrollmentWelcomeScreen`
- [ ] `PhoneVerifyScreen`
- [ ] `DOBVerifyScreen`
- [ ] `MandateAcceptanceScreen`
- [ ] `EnrollmentCompleteScreen`

### Provider & State Management

- [ ] Create `EnrollmentProvider`
- [ ] Handle enrollment state
- [ ] API integration

---

# PHASE 3: DOCUMENTATION WORKFLOW (Weeks 9-12)

## Week 9-10: Enhanced Check-In

### Biometric Capture

- [ ] Create `SelfieArtifact` model
- [ ] Create `BiometricCaptureService`
- [ ] Integrate liveness detection
- [ ] Create quality signal recording

### Frontend Capture Flow

- [ ] GPS capture component
- [ ] Selfie capture component
- [ ] Liveness detection UI
- [ ] Review before submit
- [ ] Receipt display

## Week 11-12: Offline & Queue

### Offline Queue

- [ ] Create encrypted SQLite queue
- [ ] Implement sync service
- [ ] Handle exponential backoff
- [ ] UI status indicators

### Dual Timestamps

- [ ] Update all models for dual timestamps
- [ ] Update API to accept device timestamp
- [ ] Display both in review interface

---

# PHASE 4: REVIEW & MESSAGING (Weeks 13-16)

## Week 13-14: Professional Review

### Review Queue Backend

- [ ] Create `ProfessionalReviewService`
- [ ] Create filtering logic
- [ ] Create decision workflow
- [ ] Add credential validation

### Review Queue Frontend (Web)

- [ ] Create review queue screen
- [ ] Create record detail view
- [ ] Create decision modal
- [ ] Integrate quality signals display

## Week 15-16: Messaging System

### Messaging Models

- [ ] Create all messaging models
- [ ] Create migrations
- [ ] Add immutability constraints

### Messaging Service & API

- [ ] Create `MessagingService`
- [ ] Create all endpoints
- [ ] Implement SLA tracking
- [ ] Create export functionality

### Messaging Frontend

- [ ] Thread list screen
- [ ] Conversation view
- [ ] Compose message
- [ ] Export options

---

# PHASE 5: REPORTS & VERIFICATION (Weeks 17-20)

## Week 17-18: Report Generation

### Report Templates

- [ ] Create template model
- [ ] Create jurisdiction-specific templates
- [ ] Implement template rendering

### Report Generation Service

- [ ] Server-side PDF generation
- [ ] QR code embedding
- [ ] Hash calculation
- [ ] Storage

## Week 19-20: Verification Framework

### Provider Interface

- [ ] Create abstract base class
- [ ] Implement VC_NATIVE provider
- [ ] Create hook points
- [ ] Feature flags for providers

### Proof Display

- [ ] Update QR viewer
- [ ] Add proof status to exports
- [ ] Create verification endpoint

---

# PHASE 6: GOVERNANCE & BILLING (Weeks 21-24)

## Week 21-22: Audit & Retention

### Audit Ledger

- [ ] Create `AuditEntry` model
- [ ] Implement hash chaining
- [ ] Create audit middleware
- [ ] Create export functionality

### Retention Management

- [ ] Create retention policy model
- [ ] Create legal hold model
- [ ] Implement scheduled deletion
- [ ] Create tombstone records

## Week 23-24: Subscriptions

### Stripe Integration

- [ ] Create subscription model
- [ ] Implement Stripe webhooks
- [ ] Create checkout session endpoint
- [ ] Handle subscription lifecycle

### Ad-Free Experience

- [ ] Check subscription status
- [ ] Hide ads for subscribers
- [ ] Handle grace periods

---

# TESTING CHECKLIST (Continuous)

## Unit Tests (Each Sprint)

- [ ] All new service methods have tests
- [ ] All new models have tests
- [ ] All new endpoints have tests
- [ ] Coverage report generated
- [ ] Coverage > 80% maintained

## Integration Tests (Each Sprint)

- [ ] API integration tests updated
- [ ] Database integration tests updated
- [ ] External service mocks updated

## End-to-End Tests (Phase End)

- [ ] Complete user journey tested
- [ ] Professional workflow tested
- [ ] Error scenarios tested

---

# DEPLOYMENT CHECKLIST (Each Phase)

## Pre-Deployment

- [ ] All migrations tested locally
- [ ] All tests passing
- [ ] Security review completed
- [ ] Documentation updated

## Deployment

- [ ] Database backup created
- [ ] Migrations run successfully
- [ ] Application deployed
- [ ] Health checks passing

## Post-Deployment

- [ ] Smoke tests passing
- [ ] Monitoring confirmed
- [ ] Rollback plan confirmed

---

# CODE REVIEW CHECKLIST

## For Every PR

- [ ] Follows existing architecture patterns
- [ ] Single-line imports only
- [ ] No prohibited terminology
- [ ] Tests included
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Immutability constraints respected
- [ ] Audit logging included
- [ ] Error handling complete
- [ ] Accessibility considered

---

**END OF DEVELOPMENT CHECKLIST**

