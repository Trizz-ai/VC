# Verified Compliance™ — Enhanced Product Requirements Specification v2.0

## Document Overview

This document extends the original `epics.md` with new client requirements, establishing system-wide standards for a **documentation platform** (not automated compliance decision engine). All new features integrate with the existing FastAPI backend and Flutter frontend architecture.

---

## ARCHITECTURAL ALIGNMENT NOTES

### Existing Patterns to Follow:
- **Backend**: FastAPI 0.104+, SQLAlchemy 2.0+ async, Alembic migrations, Pydantic schemas
- **Frontend**: Flutter 3.16+, Provider/Riverpod state management, Clean Architecture
- **Database**: PostgreSQL with UUID primary keys (stored as String(36)), append-only event patterns
- **API**: RESTful `/api/v1/` prefix, JWT authentication, standardized response schemas
- **Models**: Use `String(36)` for IDs with `uuid.uuid4()` defaults, timestamp columns with timezone

### Key Constraints:
- **NO mocks, NO stubs, NO hardcoded responses** — real implementations only
- **Single-line imports only** — no multi-line or relative imports
- All timestamps stored in **UTC** with timezone metadata
- Records must be **immutable** post-submission (append-only pattern)

---

# EPIC V2-1: Core Documentation Language & Terminology Standards

## Objective
Establish system-wide language standards positioning the platform as a **documentation tool** rather than an automated compliance decision engine.

## User Story V2-1.1: Terminology Enforcement Pipeline

**As a** developer  
**I want** automated CI/CD checks for prohibited terminology  
**So that** the codebase maintains compliant language standards

### Acceptance Criteria:
- [ ] CI/CD pipeline includes terminology linting step
- [ ] Build fails if prohibited terms detected in:
  - Python source files (`*.py`)
  - Dart source files (`*.dart`)
  - UI string files (ARB/JSON)
  - Export templates
- [ ] Allowlist for legitimate technical uses (e.g., "verified_at" in internal schemas)
- [ ] Clear error messages identifying file/line of violation

### Approved Terminology:
| Use This | NOT This |
|----------|----------|
| Record | Verified |
| Document | Proven |
| Data Quality Signal | Confirmed |
| Review | Compliance Score |
| Professional Determination | Pass/Fail |
| Needs Review Attention | Verified/Unverified |

### Development Checklist:

#### Backend CI/CD Integration
- [ ] **Step 1**: Create `scripts/terminology_check.py`
  ```
  Location: backend/scripts/terminology_check.py
  Purpose: Scan source files for prohibited terms
  ```
  - [ ] 1.1: Define PROHIBITED_TERMS list: `["verified", "proven", "confirmed", "compliance score", "pass/fail"]`
  - [ ] 1.2: Define ALLOWED_CONTEXTS list: `["verified_at", "email_verified", "verification_provider"]`
  - [ ] 1.3: Implement file scanner function with regex pattern matching
  - [ ] 1.4: Implement context-aware filtering (exclude allowed technical terms)
  - [ ] 1.5: Return exit code 1 if violations found, 0 if clean
  - [ ] 1.6: Output violations in format: `{file}:{line}: Found prohibited term "{term}"`

- [ ] **Step 2**: Create GitHub Actions workflow step
  ```yaml
  Location: .github/workflows/ci.yml
  Add step after linting, before tests
  ```
  - [ ] 2.1: Add job step `terminology-check`
  - [ ] 2.2: Run Python script with glob patterns for `backend/**/*.py`
  - [ ] 2.3: Run Dart script for `frontend/**/*.dart`
  - [ ] 2.4: Fail build on non-zero exit code

- [ ] **Step 3**: Create pre-commit hook
  ```
  Location: .pre-commit-config.yaml
  ```
  - [ ] 3.1: Add terminology check as pre-commit hook
  - [ ] 3.2: Configure to run on staged files only
  - [ ] 3.3: Document in CONTRIBUTING.md

#### Frontend Terminology Scanner
- [ ] **Step 4**: Create `frontend/scripts/terminology_check.dart`
  - [ ] 4.1: Scan all `.dart` files in `lib/`
  - [ ] 4.2: Scan ARB localization files
  - [ ] 4.3: Check widget text strings
  - [ ] 4.4: Output violations to stderr

---

## User Story V2-1.2: Documentation Disclaimer Banner

**As a** user viewing any record  
**I want to** see a persistent disclaimer banner  
**So that** I understand this is documentation, not verification

### Acceptance Criteria:
- [ ] Banner displays on ALL record view screens
- [ ] Banner text: "This is a documentation record. Final determinations are made by your supervising professional."
- [ ] Banner is non-dismissible
- [ ] Banner styling: distinctive color (amber/yellow), icon indicator
- [ ] Banner persists across screen transitions within record views

### Development Checklist:

#### Backend - API Response Metadata
- [ ] **Step 1**: Add disclaimer to response schemas
  ```
  Location: backend/app/schemas/common.py
  ```
  - [ ] 1.1: Create `DisclaimerMixin` base class with `disclaimer_text` field
  - [ ] 1.2: Set default value to standard disclaimer text
  - [ ] 1.3: Add `is_documentation_record: bool = True` flag

- [ ] **Step 2**: Update session response schema
  ```
  Location: backend/app/schemas/session.py
  ```
  - [ ] 2.1: Add DisclaimerMixin to SessionResponse
  - [ ] 2.2: Add DisclaimerMixin to SessionDetails

#### Frontend - Banner Widget
- [ ] **Step 3**: Create reusable disclaimer banner widget
  ```
  Location: frontend/lib/ui/widgets/vc_disclaimer_banner.dart
  ```
  - [ ] 3.1: Create StatelessWidget `VCDisclaimerBanner`
  - [ ] 3.2: Implement amber/warning color scheme
  - [ ] 3.3: Add info icon (Icons.info_outline)
  - [ ] 3.4: Implement accessibility labels (screen reader support)
  - [ ] 3.5: Make text configurable via constructor parameter
  - [ ] 3.6: Set default text to standard disclaimer

- [ ] **Step 4**: Integrate banner into record screens
  - [ ] 4.1: Add to `SessionScreen` below app bar
  - [ ] 4.2: Add to `SessionListScreen` at top of list
  - [ ] 4.3: Add to `ReportsScreen`
  - [ ] 4.4: Add to public share page

- [ ] **Step 5**: Write widget tests
  ```
  Location: frontend/test/widgets/vc_disclaimer_banner_test.dart
  ```
  - [ ] 5.1: Test banner renders correct text
  - [ ] 5.2: Test accessibility labels present
  - [ ] 5.3: Test banner styling (color, icon)

---

## User Story V2-1.3: Immutable Review Artifacts

**As a** system  
**I want** professional decisions stored as immutable, append-only review artifacts  
**So that** original records are never mutated by review processes

### Acceptance Criteria:
- [ ] Review artifacts stored in separate table from source records
- [ ] Original records NEVER modified by review process
- [ ] Review artifacts include: decision type, reviewer ID, timestamp, reason
- [ ] All review actions create new artifact records (no updates)
- [ ] Audit trail exportable

### Development Checklist:

#### Database Model - Review Artifacts
- [ ] **Step 1**: Create ReviewArtifact model
  ```
  Location: backend/app/models/review_artifact.py
  ```
  - [ ] 1.1: Define model class `ReviewArtifact(Base)`
  - [ ] 1.2: Add `__tablename__ = "review_artifacts"`
  - [ ] 1.3: Add columns:
    - `id`: String(36), primary key, default uuid4
    - `source_record_id`: String(36), indexed (polymorphic reference)
    - `source_record_type`: String(50) (e.g., "session", "message")
    - `decision_type`: Enum (APPROVED, REJECTED, FLAGGED, ANNOTATED)
    - `reviewer_id`: String(36), ForeignKey to contacts/professionals
    - `reviewer_credential_state`: String(50)
    - `reason`: Text, nullable
    - `annotation`: Text, nullable
    - `created_at`: DateTime with timezone, server default
    - `policy_version_id`: String(36), ForeignKey
  - [ ] 1.4: Add CHECK constraint: no UPDATE allowed (via trigger)
  - [ ] 1.5: Create enum `ReviewDecisionType`

- [ ] **Step 2**: Create Alembic migration
  ```
  Location: backend/alembic/versions/XXX_add_review_artifacts.py
  ```
  - [ ] 2.1: Create `review_artifacts` table
  - [ ] 2.2: Add indexes on `source_record_id`, `reviewer_id`, `created_at`
  - [ ] 2.3: Add database trigger to prevent UPDATE operations
  - [ ] 2.4: Test migration up/down

- [ ] **Step 3**: Create ReviewArtifact schema
  ```
  Location: backend/app/schemas/review.py
  ```
  - [ ] 3.1: Create `ReviewArtifactCreate` request schema
  - [ ] 3.2: Create `ReviewArtifactResponse` response schema
  - [ ] 3.3: Validate reason required when decision_type is REJECTED

- [ ] **Step 4**: Create ReviewService
  ```
  Location: backend/app/services/review_service.py
  ```
  - [ ] 4.1: Implement `create_review_artifact()` method
  - [ ] 4.2: Implement `get_artifacts_for_record()` method
  - [ ] 4.3: Implement `export_artifacts()` method for audit export
  - [ ] 4.4: NO update or delete methods (immutable)

- [ ] **Step 5**: Create review API endpoints
  ```
  Location: backend/app/api/v1/endpoints/reviews.py
  ```
  - [ ] 5.1: `POST /api/v1/reviews` - create artifact
  - [ ] 5.2: `GET /api/v1/reviews/{record_id}` - get artifacts for record
  - [ ] 5.3: `GET /api/v1/reviews/export` - export audit trail

---

# EPIC V2-2: Account Creation, Identity Verification & 2FA

## Objective
Implement secure account creation with mandatory two-factor authentication while minimizing identity data collection.

## User Story V2-2.1: Mandatory 2FA Before First Check-In

**As a** new user  
**I want to** be required to set up 2FA before I can check in  
**So that** my account is secure from the start

### Acceptance Criteria:
- [ ] Check-in functionality disabled until 2FA configured
- [ ] Phone number verification required
- [ ] Email verification required  
- [ ] Clear UI indication of 2FA setup requirement
- [ ] Progress indicator showing verification steps
- [ ] Re-verification possible if phone/email changes

### Development Checklist:

#### Database Model - 2FA Status
- [ ] **Step 1**: Extend Contact model for 2FA
  ```
  Location: backend/app/models/contact.py
  ```
  - [ ] 1.1: Add column `phone_verified: Boolean, default=False`
  - [ ] 1.2: Add column `phone_verified_at: DateTime, nullable=True`
  - [ ] 1.3: Add column `email_verified: Boolean, default=False`
  - [ ] 1.4: Add column `email_verified_at: DateTime, nullable=True`
  - [ ] 1.5: Add column `twofa_enabled: Boolean, default=False`
  - [ ] 1.6: Add column `twofa_setup_completed_at: DateTime, nullable=True`
  - [ ] 1.7: Add property `is_2fa_complete` returning `phone_verified and email_verified and twofa_enabled`

- [ ] **Step 2**: Create VerificationCode model
  ```
  Location: backend/app/models/verification_code.py
  ```
  - [ ] 2.1: Define model class
  - [ ] 2.2: Add columns:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `code_type`: Enum (PHONE, EMAIL, TOTP_SETUP)
    - `code_hash`: String(255) - store hashed codes
    - `expires_at`: DateTime
    - `used_at`: DateTime, nullable
    - `attempts`: Integer, default=0
    - `max_attempts`: Integer, default=3
  - [ ] 2.3: Add method `is_valid()` checking expiry and attempts
  - [ ] 2.4: Add method `mark_used()`

- [ ] **Step 3**: Create Alembic migration
  - [ ] 3.1: Add new columns to contacts table
  - [ ] 3.2: Create verification_codes table
  - [ ] 3.3: Add indexes

#### Backend - Verification Service
- [ ] **Step 4**: Create VerificationService
  ```
  Location: backend/app/services/verification_service.py
  ```
  - [ ] 4.1: Implement `generate_phone_code(contact_id)` - returns 6-digit code
  - [ ] 4.2: Implement `verify_phone_code(contact_id, code)` - validates and marks verified
  - [ ] 4.3: Implement `generate_email_code(contact_id)` - returns 6-digit code
  - [ ] 4.4: Implement `verify_email_code(contact_id, code)`
  - [ ] 4.5: Implement `setup_totp(contact_id)` - generates TOTP secret
  - [ ] 4.6: Implement `verify_totp(contact_id, token)`
  - [ ] 4.7: Integrate with SMS service (Twilio/similar)
  - [ ] 4.8: Integrate with email service

- [ ] **Step 5**: Create verification API endpoints
  ```
  Location: backend/app/api/v1/endpoints/verification.py
  ```
  - [ ] 5.1: `POST /api/v1/verification/phone/send` - send SMS code
  - [ ] 5.2: `POST /api/v1/verification/phone/verify` - verify SMS code
  - [ ] 5.3: `POST /api/v1/verification/email/send` - send email code
  - [ ] 5.4: `POST /api/v1/verification/email/verify` - verify email code
  - [ ] 5.5: `POST /api/v1/verification/totp/setup` - get TOTP QR code
  - [ ] 5.6: `POST /api/v1/verification/totp/verify` - verify TOTP token
  - [ ] 5.7: `GET /api/v1/verification/status` - get verification status

- [ ] **Step 6**: Add 2FA check to session endpoints
  ```
  Location: backend/app/api/v1/endpoints/sessions.py
  ```
  - [ ] 6.1: Create dependency `require_2fa_complete`
  - [ ] 6.2: Apply to check-in endpoint
  - [ ] 6.3: Return 403 with `{"error": "2FA_REQUIRED", "message": "..."}` if not complete

#### Frontend - 2FA Setup Flow
- [ ] **Step 7**: Create 2FA setup screens
  ```
  Location: frontend/lib/ui/screens/auth/
  ```
  - [ ] 7.1: Create `PhoneVerificationScreen`
    - Input field for phone number
    - "Send Code" button
    - Code input field (6 digits)
    - "Verify" button
    - Resend code option with cooldown timer
  - [ ] 7.2: Create `EmailVerificationScreen`
    - Similar structure to phone verification
  - [ ] 7.3: Create `TotpSetupScreen`
    - QR code display
    - Manual entry option
    - Code verification input
  - [ ] 7.4: Create `TwoFactorProgressScreen`
    - Stepper widget showing progress
    - Navigate through verification steps

- [ ] **Step 8**: Update AuthProvider
  ```
  Location: frontend/lib/features/auth/providers/auth_provider.dart
  ```
  - [ ] 8.1: Add `is2FAComplete` getter
  - [ ] 8.2: Add `verificationStatus` state
  - [ ] 8.3: Implement verification methods
  - [ ] 8.4: Block navigation to check-in if 2FA incomplete

- [ ] **Step 9**: Update app routing
  ```
  Location: frontend/lib/app/routes.dart
  ```
  - [ ] 9.1: Add route guard for 2FA status
  - [ ] 9.2: Redirect to 2FA setup if incomplete
  - [ ] 9.3: Add verification routes

---

## User Story V2-2.2: Required Consent Artifacts

**As a** new user  
**I want to** provide explicit consent for data collection  
**So that** my data rights are protected

### Acceptance Criteria:
- [ ] Biometric data capture consent required
- [ ] Location data capture consent required
- [ ] Data retention policy disclosure shown
- [ ] "Documentation, not verification" legal disclosure shown
- [ ] All consents timestamped and stored
- [ ] Consent artifacts exportable

### Development Checklist:

#### Database Model - Consent Artifacts
- [ ] **Step 1**: Create ConsentArtifact model
  ```
  Location: backend/app/models/consent_artifact.py
  ```
  - [ ] 1.1: Define model class
  - [ ] 1.2: Add columns:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `consent_type`: Enum (BIOMETRIC, LOCATION, DATA_RETENTION, DOCUMENTATION_DISCLOSURE)
    - `consent_version`: String(20) - policy version
    - `consent_text_hash`: String(64) - SHA256 of consent text shown
    - `granted`: Boolean
    - `granted_at`: DateTime
    - `ip_address`: String(45), nullable
    - `user_agent`: String(500), nullable
    - `device_id`: String(100), nullable
  - [ ] 1.3: Make records immutable (no UPDATE)

- [ ] **Step 2**: Create migration
  - [ ] 2.1: Create `consent_artifacts` table
  - [ ] 2.2: Add composite index on `contact_id, consent_type`

- [ ] **Step 3**: Create ConsentService
  ```
  Location: backend/app/services/consent_service.py
  ```
  - [ ] 3.1: Implement `record_consent(contact_id, consent_type, granted, context)`
  - [ ] 3.2: Implement `get_consents(contact_id)`
  - [ ] 3.3: Implement `has_all_required_consents(contact_id)`
  - [ ] 3.4: Implement `export_consents(contact_id)` - for data export requests

- [ ] **Step 4**: Create consent API endpoints
  ```
  Location: backend/app/api/v1/endpoints/consent.py
  ```
  - [ ] 4.1: `POST /api/v1/consent` - record consent
  - [ ] 4.2: `GET /api/v1/consent` - get user's consents
  - [ ] 4.3: `GET /api/v1/consent/required` - get required consent types
  - [ ] 4.4: `GET /api/v1/consent/export` - export consent artifacts

#### Frontend - Consent Collection
- [ ] **Step 5**: Create consent screens
  ```
  Location: frontend/lib/ui/screens/auth/consent/
  ```
  - [ ] 5.1: Create `ConsentFlowScreen` - orchestrates consent collection
  - [ ] 5.2: Create `BiometricConsentScreen`
    - Explain what biometric data is collected
    - Show data retention policy
    - Checkbox + signature area
  - [ ] 5.3: Create `LocationConsentScreen`
    - Explain when location is captured
    - Emphasize "only during check-in/out"
    - Checkbox + signature area
  - [ ] 5.4: Create `DocumentationDisclaimerScreen`
    - Clear legal language
    - "I understand this is documentation, not verification"
    - Required acknowledgment

- [ ] **Step 6**: Update registration flow
  - [ ] 6.1: Insert consent flow after contact creation
  - [ ] 6.2: Block progression until all consents granted
  - [ ] 6.3: Store consent status in local storage

---

## User Story V2-2.3: Minimal Identity Data Schema

**As a** system  
**I want** to collect only minimal identity data  
**So that** user privacy is maximized

### Acceptance Criteria:
- [ ] Required fields only: full name, DOB (jurisdiction-dependent), jurisdiction ID
- [ ] Optional: supervising office ID, case ID
- [ ] No unnecessary PII collected
- [ ] Data schema enforces minimal required fields

### Development Checklist:

#### Backend - Identity Schema
- [ ] **Step 1**: Create UserIdentity model
  ```
  Location: backend/app/models/user_identity.py
  ```
  - [ ] 1.1: Define model with minimal fields:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey, unique
    - `full_name`: String(255), required
    - `date_of_birth`: Date, nullable (jurisdiction-dependent)
    - `jurisdiction_id`: String(36), ForeignKey, required
    - `supervising_office_id`: String(36), nullable
    - `case_identifier`: String(100), nullable
    - `created_at`: DateTime
  - [ ] 1.2: Add relationship to Contact model

- [ ] **Step 2**: Create Jurisdiction model
  ```
  Location: backend/app/models/jurisdiction.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `name`: String(255)
    - `code`: String(20), unique
    - `requires_dob`: Boolean, default=True
    - `timezone`: String(50)
    - `policy_version_id`: String(36), ForeignKey
  - [ ] 2.2: Seed with initial jurisdictions

- [ ] **Step 3**: Create migration
  - [ ] 3.1: Create `user_identities` table
  - [ ] 3.2: Create `jurisdictions` table
  - [ ] 3.3: Add foreign key from contacts to user_identities

- [ ] **Step 4**: Update contact creation endpoint
  - [ ] 4.1: Accept identity data in registration
  - [ ] 4.2: Validate DOB requirement based on jurisdiction
  - [ ] 4.3: Create identity record atomically with contact

---

# EPIC V2-3: Mandate Initiation & SMS-Based Enrollment

## Objective
Enable professionals to initiate mandates via web portal and securely enroll individuals via SMS.

## User Story V2-3.1: Professional Mandate Creation

**As a** professional  
**I want to** create mandate records via web portal  
**So that** I can enroll individuals for documentation

### Acceptance Criteria:
- [ ] Professional can create mandate record with individual details
- [ ] System generates single-use enrollment token
- [ ] Token contains: mandate ID, expiration (7 days default), single-use flag
- [ ] Token delivered via SMS with app store links
- [ ] SMS delivery status tracked
- [ ] Professional can view mandate status

### Development Checklist:

#### Database Model - Mandates
- [ ] **Step 1**: Create Mandate model
  ```
  Location: backend/app/models/mandate.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `professional_id`: String(36), ForeignKey to contacts
    - `individual_phone`: String(20), required
    - `individual_name`: String(255)
    - `individual_dob`: Date, nullable
    - `status`: Enum (CREATED, TOKEN_SENT, ENROLLED, EXPIRED, CANCELLED)
    - `created_at`: DateTime
    - `enrolled_at`: DateTime, nullable
    - `enrolled_contact_id`: String(36), ForeignKey, nullable
  - [ ] 1.2: Add relationship to Professional

- [ ] **Step 2**: Create EnrollmentToken model
  ```
  Location: backend/app/models/enrollment_token.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `mandate_id`: String(36), ForeignKey
    - `token_hash`: String(64) - SHA256 of token
    - `expires_at`: DateTime
    - `is_single_use`: Boolean, default=True
    - `used_at`: DateTime, nullable
    - `created_at`: DateTime

- [ ] **Step 3**: Create SMSDeliveryLog model
  ```
  Location: backend/app/models/sms_delivery_log.py
  ```
  - [ ] 3.1: Define model:
    - `id`: String(36), primary key
    - `mandate_id`: String(36), ForeignKey
    - `phone_number`: String(20)
    - `message_type`: Enum (ENROLLMENT, REMINDER)
    - `provider_message_id`: String(100)
    - `status`: Enum (QUEUED, SENT, DELIVERED, FAILED)
    - `status_updated_at`: DateTime
    - `error_message`: Text, nullable

- [ ] **Step 4**: Create migration
  - [ ] 4.1: Create `mandates` table
  - [ ] 4.2: Create `enrollment_tokens` table
  - [ ] 4.3: Create `sms_delivery_logs` table

#### Backend - Mandate Service
- [ ] **Step 5**: Create MandateService
  ```
  Location: backend/app/services/mandate_service.py
  ```
  - [ ] 5.1: Implement `create_mandate(professional_id, individual_data)`
  - [ ] 5.2: Implement `generate_enrollment_token(mandate_id)` - creates secure token
  - [ ] 5.3: Implement `send_enrollment_sms(mandate_id)` - sends SMS with token
  - [ ] 5.4: Implement `validate_token(token)` - checks validity, returns mandate
  - [ ] 5.5: Implement `complete_enrollment(token, contact_id)` - marks used
  - [ ] 5.6: Implement `get_mandates_by_professional(professional_id)`

- [ ] **Step 6**: Create SMS integration
  ```
  Location: backend/app/services/sms_service.py
  ```
  - [ ] 6.1: Implement Twilio/SMS provider integration
  - [ ] 6.2: Implement `send_sms(phone, message)`
  - [ ] 6.3: Implement delivery webhook handler
  - [ ] 6.4: Log all SMS attempts

- [ ] **Step 7**: Create mandate API endpoints
  ```
  Location: backend/app/api/v1/endpoints/mandates.py
  ```
  - [ ] 7.1: `POST /api/v1/mandates` - create mandate (professional only)
  - [ ] 7.2: `GET /api/v1/mandates` - list mandates (professional only)
  - [ ] 7.3: `GET /api/v1/mandates/{id}` - get mandate details
  - [ ] 7.4: `POST /api/v1/mandates/{id}/send-sms` - send/resend enrollment SMS
  - [ ] 7.5: `POST /api/v1/mandates/enroll` - validate token and enroll (public)

---

## User Story V2-3.2: Mobile Enrollment via Deep Link

**As an** individual  
**I want to** enroll via SMS link  
**So that** I can quickly set up my account

### Acceptance Criteria:
- [ ] Deep link captures enrollment token from SMS
- [ ] Phone number verified against mandate record
- [ ] DOB soft-verified
- [ ] 2FA setup completed
- [ ] Consent artifacts captured
- [ ] Mandate details displayed and acceptance captured

### Development Checklist:

#### Frontend - Enrollment Flow
- [ ] **Step 1**: Configure deep link handling
  ```
  Location: frontend/lib/app/deep_link_handler.dart
  ```
  - [ ] 1.1: Register URI scheme `verifiedcompliance://`
  - [ ] 1.2: Handle path `/enroll?token={token}`
  - [ ] 1.3: Parse token from query parameters
  - [ ] 1.4: Navigate to enrollment screen with token

- [ ] **Step 2**: Create enrollment screens
  ```
  Location: frontend/lib/ui/screens/enrollment/
  ```
  - [ ] 2.1: Create `EnrollmentWelcomeScreen`
    - Display mandate details
    - "Continue" button
  - [ ] 2.2: Create `PhoneVerifyScreen`
    - Pre-fill phone from mandate
    - Request SMS code
    - Verify code
  - [ ] 2.3: Create `DOBVerifyScreen`
    - Date picker for DOB entry
    - Soft-verify against mandate record
  - [ ] 2.4: Create `MandateAcceptanceScreen`
    - Display full mandate details
    - Checkbox acknowledgment
    - "Accept & Continue" button

- [ ] **Step 3**: Create EnrollmentProvider
  ```
  Location: frontend/lib/features/enrollment/providers/enrollment_provider.dart
  ```
  - [ ] 3.1: Manage enrollment state
  - [ ] 3.2: Call backend APIs for validation
  - [ ] 3.3: Track progress through enrollment steps
  - [ ] 3.4: Handle errors and retries

- [ ] **Step 4**: Integration tests
  - [ ] 4.1: Test complete enrollment flow
  - [ ] 4.2: Test invalid token handling
  - [ ] 4.3: Test expired token handling
  - [ ] 4.4: Test phone mismatch handling

---

# EPIC V2-4: Check-In/Check-Out Documentation Workflow

## Objective
Implement time-bounded documentation capture workflow **without** automated compliance determinations.

## User Story V2-4.1: User-Initiated Check-In (Arrival) Capture

**As a** user  
**I want to** manually initiate check-in  
**So that** I have control over when my arrival is documented

### Acceptance Criteria:
- [ ] Scheduled window with configurable grace period
- [ ] Selfie capture with liveness detection
- [ ] GPS location snapshot (single capture, not continuous)
- [ ] Optional context notes (user-provided)
- [ ] User must explicitly submit (no auto-submission)
- [ ] Receipt generated for each submission

### Development Checklist:

#### Backend - Enhanced Session Events
- [ ] **Step 1**: Extend SessionEvent model
  ```
  Location: backend/app/models/session_event.py
  ```
  - [ ] 1.1: Add column `selfie_artifact_id`: String(36), ForeignKey, nullable
  - [ ] 1.2: Add column `liveness_score`: Float, nullable
  - [ ] 1.3: Add column `liveness_passed`: Boolean, nullable
  - [ ] 1.4: Add column `device_timestamp`: DateTime - device's local time
  - [ ] 1.5: Add column `server_receipt_timestamp`: DateTime - server receipt time
  - [ ] 1.6: Add column `context_notes`: Text, nullable
  - [ ] 1.7: Add column `receipt_id`: String(36), unique

- [ ] **Step 2**: Create SelfieArtifact model
  ```
  Location: backend/app/models/selfie_artifact.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `session_event_id`: String(36), ForeignKey, nullable
    - `file_hash`: String(64) - SHA256 of image
    - `storage_path`: String(500)
    - `captured_at`: DateTime
    - `liveness_provider`: String(50)
    - `liveness_result`: JSON - raw result from provider
    - `blur_score`: Float, nullable
    - `lighting_quality`: Float, nullable
    - `occlusion_detected`: Boolean, nullable

- [ ] **Step 3**: Create migration
  - [ ] 3.1: Add new columns to session_events
  - [ ] 3.2: Create selfie_artifacts table

- [ ] **Step 4**: Create BiometricCaptureService
  ```
  Location: backend/app/services/biometric_capture_service.py
  ```
  - [ ] 4.1: Implement `process_selfie(image_data, contact_id)`
  - [ ] 4.2: Integrate liveness detection API
  - [ ] 4.3: Calculate quality scores (blur, lighting)
  - [ ] 4.4: Store artifact securely
  - [ ] 4.5: Return artifact ID and quality signals

- [ ] **Step 5**: Create ReceiptService
  ```
  Location: backend/app/services/receipt_service.py
  ```
  - [ ] 5.1: Implement `generate_receipt(session_event_id)`
  - [ ] 5.2: Generate unique receipt ID
  - [ ] 5.3: Include: receipt ID, event type, timestamps, QR reference
  - [ ] 5.4: Return receipt data

- [ ] **Step 6**: Update check-in endpoint
  ```
  Location: backend/app/api/v1/endpoints/sessions.py
  ```
  - [ ] 6.1: Accept selfie image in request
  - [ ] 6.2: Accept context notes
  - [ ] 6.3: Process biometric capture
  - [ ] 6.4: Create session event with all data
  - [ ] 6.5: Generate and return receipt

#### Frontend - Check-In Flow
- [ ] **Step 7**: Create enhanced check-in screen
  ```
  Location: frontend/lib/ui/screens/checkin/check_in_capture_screen.dart
  ```
  - [ ] 7.1: GPS capture component
    - Request location permission
    - Display accuracy indicator
    - Show coordinates on map preview
  - [ ] 7.2: Selfie capture component
    - Camera preview
    - Face detection overlay
    - Liveness prompts (blink, smile)
    - Capture button
  - [ ] 7.3: Context notes input
    - Optional text field
    - Character limit (500)
  - [ ] 7.4: Review before submit
    - Show all captured data
    - Edit options
    - Clear "Submit" button
  - [ ] 7.5: Receipt display
    - Show receipt ID
    - Success confirmation

- [ ] **Step 8**: Implement liveness detection
  ```
  Location: frontend/lib/core/services/liveness_service.dart
  ```
  - [ ] 8.1: Integrate ML Kit or similar
  - [ ] 8.2: Implement blink detection
  - [ ] 8.3: Implement head movement detection
  - [ ] 8.4: Return pass/fail with confidence score

---

## User Story V2-4.2: User-Initiated Check-Out (Departure) Capture

**As a** user  
**I want to** manually initiate check-out  
**So that** my departure is documented when I choose

### Acceptance Criteria:
- [ ] User-initiated only (no automatic completion)
- [ ] GPS location snapshot
- [ ] Optional departure notes
- [ ] Independent timestamp capture
- [ ] Session remains incomplete without explicit check-out
- [ ] Duration calculated from timestamps only

### Development Checklist:

#### Backend - Check-Out Logic
- [ ] **Step 1**: Update SessionService
  ```
  Location: backend/app/services/session_service.py
  ```
  - [ ] 1.1: Remove any auto-complete logic
  - [ ] 1.2: Ensure check_out requires explicit call
  - [ ] 1.3: Calculate duration: `checkout_server_ts - checkin_server_ts`
  - [ ] 1.4: Never use device timestamps for duration (only display)

- [ ] **Step 2**: Update check-out endpoint
  - [ ] 2.1: Accept departure notes
  - [ ] 2.2: Capture GPS independently
  - [ ] 2.3: Generate receipt
  - [ ] 2.4: Update session status to SUBMITTED (not COMPLETED)

#### Frontend - Check-Out Flow
- [ ] **Step 3**: Create check-out screen
  ```
  Location: frontend/lib/ui/screens/checkin/check_out_capture_screen.dart
  ```
  - [ ] 3.1: GPS capture component
  - [ ] 3.2: Departure notes input (optional)
  - [ ] 3.3: Session summary display
  - [ ] 3.4: "Submit Check-Out" button
  - [ ] 3.5: Receipt display

---

## User Story V2-4.3: Records Immutable Post-Submission

**As a** system  
**I want** records to become immutable after submission  
**So that** audit integrity is maintained

### Acceptance Criteria:
- [ ] Records cannot be modified after submission
- [ ] No AI or background processes may auto-complete sessions
- [ ] Status transitions are append-only
- [ ] All changes create new records (corrections, annotations)

### Development Checklist:

#### Backend - Immutability Enforcement
- [ ] **Step 1**: Add database constraints
  - [ ] 1.1: Create trigger on session_events preventing UPDATE
  - [ ] 1.2: Create trigger on selfie_artifacts preventing UPDATE/DELETE
  - [ ] 1.3: Add check constraint on session status transitions

- [ ] **Step 2**: Update service layer
  - [ ] 2.1: Remove all UPDATE operations on submitted events
  - [ ] 2.2: Implement correction records as new entries
  - [ ] 2.3: Add `corrects_record_id` column for linking

- [ ] **Step 3**: API validation
  - [ ] 3.1: Reject PUT/PATCH on submitted records
  - [ ] 3.2: Return 409 Conflict for mutation attempts
  - [ ] 3.3: Provide correction endpoint instead

---

# EPIC V2-5: Offline Capture, Queueing & Network Resilience

## Objective
Prevent documentation loss due to connectivity issues.

## User Story V2-5.1: Encrypted Local Queue

**As a** user  
**I want** my check-ins to be saved locally when offline  
**So that** I don't lose documentation due to network issues

### Acceptance Criteria:
- [ ] Encrypted local queue for offline records
- [ ] Queue persists across app restarts and crashes
- [ ] Records marked "Queued" until server receipt
- [ ] Dual timestamps: device capture and server receipt
- [ ] Exponential backoff retry strategy

### Development Checklist:

#### Frontend - Offline Queue
- [ ] **Step 1**: Create OfflineQueueService
  ```
  Location: frontend/lib/core/services/offline_queue_service.dart
  ```
  - [ ] 1.1: Initialize encrypted SQLite database
  - [ ] 1.2: Implement `enqueue(record)` method
  - [ ] 1.3: Implement `dequeue()` method
  - [ ] 1.4: Implement `getQueuedRecords()` method
  - [ ] 1.5: Implement `markSynced(recordId)` method
  - [ ] 1.6: Implement `markFailed(recordId, error)` method

- [ ] **Step 2**: Create QueuedRecord model
  ```
  Location: frontend/lib/core/models/queued_record.dart
  ```
  - [ ] 2.1: Define fields:
    - `localId`: String (UUID)
    - `recordType`: Enum (CHECK_IN, CHECK_OUT, NOTE)
    - `payload`: JSON string (encrypted)
    - `deviceTimestamp`: DateTime
    - `status`: Enum (QUEUED, SYNCING, SYNCED, FAILED)
    - `attempts`: int
    - `lastAttempt`: DateTime?
    - `error`: String?

- [ ] **Step 3**: Create SyncService
  ```
  Location: frontend/lib/core/services/sync_service.dart
  ```
  - [ ] 3.1: Monitor network connectivity
  - [ ] 3.2: Implement sync loop with exponential backoff
  - [ ] 3.3: Process queue items in order
  - [ ] 3.4: Handle partial sync failures
  - [ ] 3.5: Emit sync status events

- [ ] **Step 4**: Create OfflineQueueProvider
  ```
  Location: frontend/lib/features/offline/providers/offline_queue_provider.dart
  ```
  - [ ] 4.1: Expose queue status to UI
  - [ ] 4.2: Provide sync trigger method
  - [ ] 4.3: Emit notifications on sync completion

- [ ] **Step 5**: Update UI for offline status
  - [ ] 5.1: Show "Queued" badge on pending records
  - [ ] 5.2: Show sync progress indicator
  - [ ] 5.3: Show error indicator for failed syncs
  - [ ] 5.4: Allow manual retry

#### Backend - Dual Timestamp Handling
- [ ] **Step 6**: Update session event handling
  ```
  Location: backend/app/services/session_service.py
  ```
  - [ ] 6.1: Accept `device_timestamp` in request
  - [ ] 6.2: Record `server_receipt_timestamp` on receipt
  - [ ] 6.3: Store both timestamps
  - [ ] 6.4: Use server timestamp for calculations

- [ ] **Step 7**: Update API schemas
  - [ ] 7.1: Add `device_timestamp` to request schemas
  - [ ] 7.2: Add `server_receipt_timestamp` to response schemas
  - [ ] 7.3: Add `sync_status` to response

---

# EPIC V2-6: Emergency Explanation & Contextual Documentation

## Objective
Allow individuals to provide context for missed or late check-ins without mutating original records.

## User Story V2-6.1: Emergency Explanation Records

**As a** user  
**I want to** submit an emergency explanation for a missed check-in  
**So that** I can document the reason without modifying original records

### Acceptance Criteria:
- [ ] Structured categories for explanations
- [ ] Free-text narrative field
- [ ] Optional file attachments
- [ ] Linked to scheduled check-in window
- [ ] Stored as separate, immutable record
- [ ] Original records remain unchanged

### Development Checklist:

#### Database Model - Emergency Explanations
- [ ] **Step 1**: Create EmergencyExplanation model
  ```
  Location: backend/app/models/emergency_explanation.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `scheduled_window_id`: String(36), ForeignKey, nullable
    - `session_id`: String(36), ForeignKey, nullable
    - `category`: Enum (MEDICAL, TRANSPORTATION, FAMILY_EMERGENCY, WORK, TECHNICAL, OTHER)
    - `narrative`: Text, required
    - `submitted_at`: DateTime
    - `device_timestamp`: DateTime
    - `server_receipt_timestamp`: DateTime
  - [ ] 1.2: Add immutability trigger

- [ ] **Step 2**: Create ExplanationAttachment model
  ```
  Location: backend/app/models/explanation_attachment.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `explanation_id`: String(36), ForeignKey
    - `file_hash`: String(64)
    - `file_name`: String(255)
    - `file_type`: String(100)
    - `file_size`: Integer
    - `storage_path`: String(500)
    - `uploaded_at`: DateTime

- [ ] **Step 3**: Create migration
  - [ ] 3.1: Create emergency_explanations table
  - [ ] 3.2: Create explanation_attachments table

#### Backend - Explanation Service
- [ ] **Step 4**: Create EmergencyExplanationService
  ```
  Location: backend/app/services/emergency_explanation_service.py
  ```
  - [ ] 4.1: Implement `submit_explanation(contact_id, data)`
  - [ ] 4.2: Implement `add_attachment(explanation_id, file)`
  - [ ] 4.3: Implement `get_explanations(contact_id)`
  - [ ] 4.4: Implement `get_explanation_for_window(window_id)`

- [ ] **Step 5**: Create API endpoints
  ```
  Location: backend/app/api/v1/endpoints/explanations.py
  ```
  - [ ] 5.1: `POST /api/v1/explanations` - submit explanation
  - [ ] 5.2: `POST /api/v1/explanations/{id}/attachments` - add attachment
  - [ ] 5.3: `GET /api/v1/explanations` - list explanations
  - [ ] 5.4: `GET /api/v1/explanations/{id}` - get explanation details

#### Frontend - Explanation Submission
- [ ] **Step 6**: Create explanation screens
  ```
  Location: frontend/lib/ui/screens/explanations/
  ```
  - [ ] 6.1: Create `EmergencyExplanationScreen`
    - Category dropdown
    - Narrative text area (required, min 50 chars)
    - Attachment upload option
    - Submit button
  - [ ] 6.2: Create `ExplanationHistoryScreen`
    - List of submitted explanations
    - Status indicators

---

# EPIC V2-7: Data Quality Signals Framework

## Objective
Provide explainable, deterministic quality indicators **without** making compliance conclusions.

## User Story V2-7.1: GPS Quality Signals

**As a** professional reviewer  
**I want to** see GPS quality metrics  
**So that** I can assess data quality without automated judgments

### Acceptance Criteria:
- [ ] Display: accuracy radius (meters)
- [ ] Display: time-to-first-fix (seconds)
- [ ] Display: satellite/source count
- [ ] All signals deterministic and explainable
- [ ] No compliance scoring derived from signals

### Development Checklist:

#### Backend - Quality Signals Model
- [ ] **Step 1**: Create DataQualitySignal model
  ```
  Location: backend/app/models/data_quality_signal.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `session_event_id`: String(36), ForeignKey
    - `signal_type`: Enum (GPS, BIOMETRIC, DEVICE, TEMPORAL)
    - `signal_name`: String(100)
    - `signal_value`: JSON
    - `recorded_at`: DateTime
  - [ ] 1.2: Create GPS-specific signals:
    - `gps_accuracy_meters`
    - `gps_ttff_seconds`
    - `gps_satellite_count`
    - `gps_source` (GPS, NETWORK, FUSED)

- [ ] **Step 2**: Create BiometricQualitySignal entries
  - [ ] 2.1: `liveness_quality` (pass/uncertain/fail as quality, not identity)
  - [ ] 2.2: `image_blur_score` (0-1)
  - [ ] 2.3: `lighting_quality_score` (0-1)
  - [ ] 2.4: `occlusion_detected` (true/false)

- [ ] **Step 3**: Create DeviceIntegritySignal entries
  - [ ] 3.1: `root_jailbreak_detected`
  - [ ] 3.2: `emulator_detected`
  - [ ] 3.3: `system_time_drift_seconds`

- [ ] **Step 4**: Create migration
  - [ ] 4.1: Create data_quality_signals table
  - [ ] 4.2: Add indexes

#### Backend - Quality Signal Service
- [ ] **Step 5**: Create DataQualityService
  ```
  Location: backend/app/services/data_quality_service.py
  ```
  - [ ] 5.1: Implement `record_gps_signals(event_id, gps_data)`
  - [ ] 5.2: Implement `record_biometric_signals(event_id, biometric_data)`
  - [ ] 5.3: Implement `record_device_signals(event_id, device_data)`
  - [ ] 5.4: Implement `get_signals_for_event(event_id)`
  - [ ] 5.5: NO scoring or aggregation methods

- [ ] **Step 6**: Update session event endpoints
  - [ ] 6.1: Accept quality signal data in requests
  - [ ] 6.2: Return quality signals in responses
  - [ ] 6.3: Include signals in export

---

## User Story V2-7.2: Location Clustering (Non-Judgmental)

**As a** professional reviewer  
**I want to** see location patterns descriptively  
**So that** I have context without automated compliance determinations

### Acceptance Criteria:
- [ ] Cluster labels: "Recurring Location Pattern", "Inconsistent Location Pattern", "Insufficient Data"
- [ ] NOT visible to individuals
- [ ] Visible only in professional web review interface
- [ ] Mandatory disclaimer displayed
- [ ] No alerts or automation triggers
- [ ] No compliance scoring
- [ ] Versioned, logged, and jurisdiction-toggleable

### Development Checklist:

#### Backend - Location Clustering
- [ ] **Step 1**: Create LocationCluster model
  ```
  Location: backend/app/models/location_cluster.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `cluster_label`: Enum (RECURRING, INCONSISTENT, INSUFFICIENT_DATA)
    - `centroid_lat`: Float
    - `centroid_lng`: Float
    - `radius_meters`: Float
    - `event_count`: Integer
    - `first_seen`: DateTime
    - `last_seen`: DateTime
    - `confidence_score`: Float (internal use only)
    - `algorithm_version`: String(20)
    - `computed_at`: DateTime

- [ ] **Step 2**: Create ClusteringService
  ```
  Location: backend/app/services/clustering_service.py
  ```
  - [ ] 2.1: Implement DBSCAN or similar clustering algorithm
  - [ ] 2.2: Run on batch schedule (not real-time)
  - [ ] 2.3: Version algorithm for audit trail
  - [ ] 2.4: NO automated actions based on clustering

- [ ] **Step 3**: Create professional review endpoint
  - [ ] 3.1: `GET /api/v1/professional/contacts/{id}/clusters` (professional only)
  - [ ] 3.2: Include disclaimer in response
  - [ ] 3.3: Respect jurisdiction toggle

- [ ] **Step 4**: Add jurisdiction configuration
  - [ ] 4.1: Add `clustering_enabled` flag to jurisdiction model
  - [ ] 4.2: Check flag before returning cluster data

---

# EPIC V2-8: Professional Review & Decision Workflow (Web)

## Objective
Ensure human professionals make ALL compliance determinations with full audit trail.

## User Story V2-8.1: Review Queue Interface

**As a** professional  
**I want** a filterable review queue  
**So that** I can efficiently review documentation records

### Acceptance Criteria:
- [ ] Filter by status, individual, date range
- [ ] Display all data quality signals
- [ ] Display location clustering context (if enabled)
- [ ] Decision actions: Approve, Reject (reason required), Flag, Annotate
- [ ] Every decision creates immutable review artifact

### Development Checklist:

#### Backend - Professional Review API
- [ ] **Step 1**: Create ProfessionalReviewService
  ```
  Location: backend/app/services/professional_review_service.py
  ```
  - [ ] 1.1: Implement `get_review_queue(professional_id, filters)`
  - [ ] 1.2: Implement `get_record_details(record_id)`
  - [ ] 1.3: Implement `submit_decision(record_id, decision, reviewer_id)`
  - [ ] 1.4: Implement `add_annotation(record_id, annotation, reviewer_id)`

- [ ] **Step 2**: Create review queue endpoint
  ```
  Location: backend/app/api/v1/endpoints/professional_review.py
  ```
  - [ ] 2.1: `GET /api/v1/professional/queue` - get review queue
  - [ ] 2.2: `GET /api/v1/professional/records/{id}` - get record details
  - [ ] 2.3: `POST /api/v1/professional/records/{id}/decide` - submit decision
  - [ ] 2.4: `POST /api/v1/professional/records/{id}/annotate` - add annotation

- [ ] **Step 3**: Validate reviewer credentials
  - [ ] 3.1: Check professional is active
  - [ ] 3.2: Check credential state
  - [ ] 3.3: Log credential state with decision

#### Frontend (Web) - Review Interface
- [ ] **Step 4**: Create professional web dashboard
  ```
  Location: frontend/lib/ui/screens/professional/
  ```
  - [ ] 4.1: Create `ReviewQueueScreen`
    - Filterable list of pending reviews
    - Status badges
    - Quick actions
  - [ ] 4.2: Create `RecordDetailScreen`
    - All captured data
    - Quality signals panel
    - Clustering context (if enabled)
    - Decision buttons
  - [ ] 4.3: Create `DecisionModal`
    - Decision type selection
    - Reason input (required for reject)
    - Annotation text area
    - Submit button

---

## User Story V2-8.2: Mobile Capabilities for Professionals (View-Only)

**As a** professional  
**I want** mobile visibility into my mandates  
**So that** I can monitor status on the go

### Acceptance Criteria:
- [ ] View-only dashboard
- [ ] No mandate creation/modification on mobile
- [ ] Alerts for new submissions, explanations, SLA warnings
- [ ] Immutable, documented messaging only

### Development Checklist:

#### Frontend - Professional Mobile View
- [ ] **Step 1**: Create professional mobile screens
  ```
  Location: frontend/lib/ui/screens/professional/
  ```
  - [ ] 1.1: Create `ProfessionalDashboardScreen`
    - List of assigned mandates
    - Status indicators (read-only)
    - Tap to view details
  - [ ] 1.2: Create `MandateViewScreen`
    - Individual's submission history
    - Emergency explanations
    - NO decision buttons (view only)

- [ ] **Step 2**: Implement notifications
  - [ ] 2.1: Push notification for new submission
  - [ ] 2.2: Push notification for emergency explanation
  - [ ] 2.3: Push notification for SLA warning

- [ ] **Step 3**: Restrict actions
  - [ ] 3.1: Hide/disable all write actions on mobile
  - [ ] 3.2: Show message "Use web portal for decisions"

---

# EPIC V2-9: In-App Messaging as Documentation Records

## Objective
Replace informal communication with auditable, immutable in-app messaging that can be exported as court-ready documentation.

## User Story V2-9.1: Immutable Message Threads

**As a** user  
**I want** in-app messaging with my professional  
**So that** all communication is documented and auditable

### Acceptance Criteria:
- [ ] Messages are append-only (no edit/delete)
- [ ] Message types: Professional Request, User Question, System Notification, Emergency
- [ ] Corrections added as new messages referencing original
- [ ] Full metadata captured and stored
- [ ] Export to transcript PDF

### Development Checklist:

#### Database Model - Messaging
- [ ] **Step 1**: Create MessageThread model
  ```
  Location: backend/app/models/message_thread.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `mandate_id`: String(36), ForeignKey
    - `created_at`: DateTime
    - `status`: Enum (ACTIVE, ARCHIVED)

- [ ] **Step 2**: Create Message model
  ```
  Location: backend/app/models/message.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `thread_id`: String(36), ForeignKey
    - `sender_id`: String(36), ForeignKey
    - `sender_role`: Enum (INDIVIDUAL, PROFESSIONAL, SYSTEM)
    - `recipient_role`: Enum
    - `message_type`: Enum (PROFESSIONAL_REQUEST, USER_QUESTION, SYSTEM_NOTIFICATION, EMERGENCY, CORRECTION)
    - `content`: Text
    - `references_message_id`: String(36), nullable (for corrections)
    - `sent_at`: DateTime
    - `device_info`: JSON
    - `app_version`: String(20)
  - [ ] 2.2: Add immutability trigger (no UPDATE/DELETE)

- [ ] **Step 3**: Create MessageAttachment model
  ```
  Location: backend/app/models/message_attachment.py
  ```
  - [ ] 3.1: Define model:
    - `id`: String(36), primary key
    - `message_id`: String(36), ForeignKey
    - `file_hash`: String(64)
    - `file_name`: String(255)
    - `file_type`: String(100)
    - `file_size`: Integer
    - `storage_path`: String(500)
    - `virus_scanned`: Boolean
    - `virus_scan_result`: String(50)

- [ ] **Step 4**: Create SLATracking model
  ```
  Location: backend/app/models/sla_tracking.py
  ```
  - [ ] 4.1: Define model:
    - `id`: String(36), primary key
    - `message_id`: String(36), ForeignKey (for Professional Requests)
    - `sla_state`: Enum (OPEN, RESPONDED, CLOSED)
    - `opened_at`: DateTime
    - `responded_at`: DateTime, nullable
    - `closed_at`: DateTime, nullable
    - `sla_deadline`: DateTime
    - `is_overdue`: Boolean

- [ ] **Step 5**: Create migration
  - [ ] 5.1: Create message_threads table
  - [ ] 5.2: Create messages table
  - [ ] 5.3: Create message_attachments table
  - [ ] 5.4: Create sla_tracking table

#### Backend - Messaging Service
- [ ] **Step 6**: Create MessagingService
  ```
  Location: backend/app/services/messaging_service.py
  ```
  - [ ] 6.1: Implement `create_thread(mandate_id)`
  - [ ] 6.2: Implement `send_message(thread_id, sender_id, content, type)`
  - [ ] 6.3: Implement `add_attachment(message_id, file)`
  - [ ] 6.4: Implement `get_thread_messages(thread_id)`
  - [ ] 6.5: Implement `update_sla_state(message_id, new_state)`

- [ ] **Step 7**: Create messaging API endpoints
  ```
  Location: backend/app/api/v1/endpoints/messages.py
  ```
  - [ ] 7.1: `POST /api/v1/messages/threads` - create thread
  - [ ] 7.2: `GET /api/v1/messages/threads/{id}` - get thread
  - [ ] 7.3: `POST /api/v1/messages/threads/{id}/messages` - send message
  - [ ] 7.4: `POST /api/v1/messages/{id}/attachments` - add attachment
  - [ ] 7.5: `GET /api/v1/messages/threads` - list threads

---

## User Story V2-9.2: Message Export & VC Report Integration

**As a** user  
**I want** to export messages as documentation transcripts  
**So that** I have court-ready records

### Acceptance Criteria:
- [ ] Export single message, selected messages, entire thread, date range
- [ ] Transcript PDF with full metadata
- [ ] Optional attachment to VC Report with QR verification
- [ ] All export actions logged

### Development Checklist:

#### Backend - Export Service
- [ ] **Step 1**: Create MessageExportService
  ```
  Location: backend/app/services/message_export_service.py
  ```
  - [ ] 1.1: Implement `export_transcript(thread_id, message_ids, format)`
  - [ ] 1.2: Generate PDF with:
    - Header: participants, roles, date range
    - Messages with timestamps, types, sender info
    - Attachment list with hashes
    - Export ID and generation timestamp
    - Page numbers
  - [ ] 1.3: Implement async generation for large exports
  - [ ] 1.4: Log all export actions

- [ ] **Step 2**: Create VCReportAttachment model
  ```
  Location: backend/app/models/vc_report_attachment.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `vc_report_id`: String(36), ForeignKey
    - `message_export_id`: String(36), ForeignKey
    - `export_hash`: String(64)
    - `attached_at`: DateTime

- [ ] **Step 3**: Create export API endpoints
  - [ ] 3.1: `POST /api/v1/messages/export` - create export
  - [ ] 3.2: `GET /api/v1/messages/exports/{id}` - get export
  - [ ] 3.3: `POST /api/v1/messages/exports/{id}/attach-to-report` - attach to VC report

#### Frontend - Message UI
- [ ] **Step 4**: Create messaging screens
  ```
  Location: frontend/lib/ui/screens/messages/
  ```
  - [ ] 4.1: Create `ThreadListScreen` - list of message threads
  - [ ] 4.2: Create `ThreadScreen` - message conversation view
  - [ ] 4.3: Create `ComposeMessageScreen` - send new message
  - [ ] 4.4: Create `ExportOptionsModal` - export selection

---

# EPIC V2-10: Reporting, Exports & QR Verification

## Objective
Generate defensible documentation packages with cryptographic integrity verification.

## User Story V2-10.1: Server-Side PDF Generation

**As a** user  
**I want** reports generated server-side  
**So that** integrity is maintained

### Acceptance Criteria:
- [ ] Server-side PDF generation only (no client-side)
- [ ] Jurisdiction-specific templates
- [ ] Embedded QR verification code
- [ ] QR confirms record existence and hash validity
- [ ] Share functionality disabled for mandated individuals

### Development Checklist:

#### Backend - Report Generation
- [ ] **Step 1**: Create ReportTemplate model
  ```
  Location: backend/app/models/report_template.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `jurisdiction_id`: String(36), ForeignKey
    - `template_name`: String(100)
    - `template_version`: String(20)
    - `template_html`: Text
    - `is_active`: Boolean
    - `created_at`: DateTime

- [ ] **Step 2**: Create VCReport model
  ```
  Location: backend/app/models/vc_report.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `session_ids`: JSON array
    - `template_id`: String(36), ForeignKey
    - `report_hash`: String(64)
    - `qr_verification_token`: String(100), unique
    - `generated_at`: DateTime
    - `pdf_storage_path`: String(500)

- [ ] **Step 3**: Create ReportGenerationService
  ```
  Location: backend/app/services/report_generation_service.py
  ```
  - [ ] 3.1: Implement `generate_report(contact_id, session_ids, template_id)`
  - [ ] 3.2: Render HTML template with data
  - [ ] 3.3: Convert to PDF (WeasyPrint or similar)
  - [ ] 3.4: Calculate report hash
  - [ ] 3.5: Generate QR code with verification token
  - [ ] 3.6: Store PDF and create record

- [ ] **Step 4**: Create QR verification endpoint
  ```
  Location: backend/app/api/v1/endpoints/public.py
  ```
  - [ ] 4.1: `GET /api/v1/public/verify/{token}` - verify QR code
  - [ ] 4.2: Return: record exists, hash valid, timestamp
  - [ ] 4.3: Do NOT assert truth or compliance status

---

# EPIC V2-11: Legal, Audit & Chain-of-Custody Controls

## Objective
Support admissibility as business records under applicable evidence rules.

## User Story V2-11.1: Append-Only Audit Ledger

**As a** system  
**I want** all actions logged in append-only audit ledger  
**So that** records are admissible as business records

### Acceptance Criteria:
- [ ] Zero gaps in audit log
- [ ] Cryptographic hash chaining
- [ ] All record views logged
- [ ] All exports logged
- [ ] All access logged
- [ ] Audit logs exportable

### Development Checklist:

#### Backend - Audit Ledger
- [ ] **Step 1**: Create AuditEntry model
  ```
  Location: backend/app/models/audit_entry.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `sequence_number`: BigInteger, unique, auto-increment
    - `action_type`: String(50)
    - `actor_id`: String(36), nullable
    - `actor_type`: Enum (USER, PROFESSIONAL, SYSTEM, ADMIN)
    - `target_type`: String(50)
    - `target_id`: String(36)
    - `action_data`: JSON
    - `ip_address`: String(45), nullable
    - `user_agent`: String(500), nullable
    - `timestamp`: DateTime
    - `previous_hash`: String(64)
    - `entry_hash`: String(64)

- [ ] **Step 2**: Create AuditService
  ```
  Location: backend/app/services/audit_service.py
  ```
  - [ ] 2.1: Implement `log_action(action_type, actor, target, data)`
  - [ ] 2.2: Calculate hash: SHA256(sequence + previous_hash + timestamp + action_data)
  - [ ] 2.3: Chain to previous entry
  - [ ] 2.4: NO update or delete methods
  - [ ] 2.5: Implement `verify_chain_integrity()`
  - [ ] 2.6: Implement `export_audit_log(date_range, format)`

- [ ] **Step 3**: Create audit middleware
  - [ ] 3.1: Log all API requests
  - [ ] 3.2: Log all data access
  - [ ] 3.3: Log all exports
  - [ ] 3.4: Log all authentication events

---

# EPIC V2-12: Advertising & Monetization (Strict Isolation)

## Objective
Enable revenue generation without compromising documentation integrity.

## User Story V2-12.1: Isolated Ad Zones

**As a** system  
**I want** ads strictly isolated from compliance flows  
**So that** documentation integrity is never compromised

### Acceptance Criteria:
- [ ] Ads allowed: home screen, non-critical info screens
- [ ] Ads prohibited: check-in/out flows, biometric capture, emergency explanations, review interfaces
- [ ] Separate analytics datastore for ad metrics
- [ ] No cross-contamination with compliance data

### Development Checklist:

#### Frontend - Ad Integration
- [ ] **Step 1**: Create AdZoneConfig
  ```
  Location: frontend/lib/core/config/ad_zones.dart
  ```
  - [ ] 1.1: Define ALLOWED_AD_SCREENS list
  - [ ] 1.2: Define PROHIBITED_AD_SCREENS list
  - [ ] 1.3: Create helper `canShowAds(screenName)`

- [ ] **Step 2**: Create AdService
  ```
  Location: frontend/lib/core/services/ad_service.dart
  ```
  - [ ] 2.1: Initialize separate analytics instance
  - [ ] 2.2: NO access to compliance data
  - [ ] 2.3: Implement `shouldShowAd(screenContext)`
  - [ ] 2.4: Block ad display on prohibited screens

- [ ] **Step 3**: Create AdBanner widget
  ```
  Location: frontend/lib/ui/widgets/ad_banner.dart
  ```
  - [ ] 3.1: Check screen permission before rendering
  - [ ] 3.2: Use isolated analytics only
  - [ ] 3.3: Handle ad-free subscription state

---

# EPIC V2-13: AI Concierge (Support-Only, Guardrailed)

## Objective
Provide AI-assisted support for comprehension and troubleshooting without making compliance determinations.

## User Story V2-13.1: Guardrailed AI Assistant

**As a** user  
**I want** AI help with app usage  
**So that** I can get quick answers to questions

### Acceptance Criteria:
- [ ] Allowed: onboarding guidance, troubleshooting, explanation drafting
- [ ] Prohibited: compliance determinations, predictions
- [ ] Disclaimer on all AI content
- [ ] PII redaction before API calls
- [ ] All AI interactions logged separately

### Development Checklist:

#### Backend - AI Service
- [ ] **Step 1**: Update AIService with guardrails
  ```
  Location: backend/app/services/ai_service.py
  ```
  - [ ] 1.1: Implement PII redaction pipeline
  - [ ] 1.2: Add system prompt enforcing guardrails
  - [ ] 1.3: Block compliance-related queries
  - [ ] 1.4: Log all interactions to separate table
  - [ ] 1.5: Add disclaimer to all responses

- [ ] **Step 2**: Create AIInteractionLog model
  ```
  Location: backend/app/models/ai_interaction_log.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `query_hash`: String(64) (hash of redacted query)
    - `response_hash`: String(64)
    - `query_type`: String(50)
    - `blocked`: Boolean
    - `block_reason`: String(100), nullable
    - `timestamp`: DateTime

- [ ] **Step 3**: Create AI content disclaimer
  - [ ] 3.1: Add to all AI response schemas
  - [ ] 3.2: Display prominently in UI

---

# EPIC V2-14: Jurisdictional Policy Engine & Versioning

## Objective
Support jurisdiction-specific variations with full auditability.

## User Story V2-14.1: Versioned Policy Configuration

**As a** system  
**I want** versioned policy configurations  
**So that** records reference the correct policy version

### Acceptance Criteria:
- [ ] Versioned policy configurations
- [ ] Feature flags per jurisdiction
- [ ] Emergency kill switches
- [ ] Each record references policy version at capture time
- [ ] Historical versions retained indefinitely

### Development Checklist:

#### Backend - Policy Engine
- [ ] **Step 1**: Create PolicyVersion model
  ```
  Location: backend/app/models/policy_version.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `jurisdiction_id`: String(36), ForeignKey
    - `version`: String(20)
    - `effective_from`: DateTime
    - `effective_until`: DateTime, nullable
    - `config`: JSON (feature flags, thresholds, etc.)
    - `created_at`: DateTime
    - `created_by`: String(36)

- [ ] **Step 2**: Create PolicyService
  ```
  Location: backend/app/services/policy_service.py
  ```
  - [ ] 2.1: Implement `get_active_policy(jurisdiction_id)`
  - [ ] 2.2: Implement `get_policy_at_time(jurisdiction_id, timestamp)`
  - [ ] 2.3: Implement `create_policy_version(jurisdiction_id, config)`
  - [ ] 2.4: Implement kill switch activation/logging

- [ ] **Step 3**: Update session event creation
  - [ ] 3.1: Capture `policy_version_id` on every event
  - [ ] 3.2: Store immutably with record

---

# EPIC V2-15: Accessibility, Inclusivity & Accommodations

## Objective
Prevent disparate impact and ensure equitable access.

## User Story V2-15.1: WCAG 2.1 AA Compliance

**As a** user with accessibility needs  
**I want** full accessibility support  
**So that** I can use the app effectively

### Acceptance Criteria:
- [ ] WCAG 2.1 AA compliance
- [ ] Plain-language mode
- [ ] Screen reader support
- [ ] High-contrast modes
- [ ] Configurable text sizing
- [ ] Alternative capture methods (policy-approved)

### Development Checklist:

#### Frontend - Accessibility
- [ ] **Step 1**: Audit and fix accessibility issues
  - [ ] 1.1: Run automated accessibility checks
  - [ ] 1.2: Test with screen readers (TalkBack, VoiceOver)
  - [ ] 1.3: Verify color contrast ratios ≥4.5:1
  - [ ] 1.4: Ensure min touch target 48dp

- [ ] **Step 2**: Implement accessibility features
  - [ ] 2.1: Add semantic labels to all widgets
  - [ ] 2.2: Implement plain-language mode toggle
  - [ ] 2.3: Implement high-contrast theme
  - [ ] 2.4: Implement text scaling support

---

# EPIC V2-16: System Resilience, Incidents & Edge Cases

## Objective
Differentiate system failures from user behavior.

## User Story V2-16.1: Incident Management

**As a** system  
**I want** incidents tracked and associated with affected records  
**So that** system failures don't penalize users

### Acceptance Criteria:
- [ ] Unique incident IDs per outage
- [ ] System downtime banners visible to all users
- [ ] Automatic incident association with affected records
- [ ] Crash recovery preserves queued records

### Development Checklist:

#### Backend - Incident Tracking
- [ ] **Step 1**: Create Incident model
  ```
  Location: backend/app/models/incident.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `incident_type`: Enum (OUTAGE, DEGRADATION, MAINTENANCE)
    - `started_at`: DateTime
    - `ended_at`: DateTime, nullable
    - `affected_services`: JSON array
    - `description`: Text
    - `severity`: Enum (CRITICAL, HIGH, MEDIUM, LOW)

- [ ] **Step 2**: Create IncidentService
  - [ ] 2.1: Implement `create_incident(type, services, description)`
  - [ ] 2.2: Implement `resolve_incident(incident_id)`
  - [ ] 2.3: Implement `get_active_incidents()`
  - [ ] 2.4: Implement `associate_record_with_incident(record_id, incident_id)`

- [ ] **Step 3**: Create incident endpoint
  - [ ] 3.1: `GET /api/v1/system/incidents/active` - get active incidents
  - [ ] 3.2: Display banner in app when incidents active

---

# EPIC V2-17: Record Lifecycle, Retention & Legal Hold

## Objective
Ensure records are retained and deleted according to policy.

## User Story V2-17.1: Retention Management

**As a** system  
**I want** automatic retention rules  
**So that** records are properly managed

### Acceptance Criteria:
- [ ] Retention rules configurable by jurisdiction and record type
- [ ] Automatic deletion when retention expires (unless on hold)
- [ ] Cryptographic erasure logged and verifiable
- [ ] Tombstone metadata retained after deletion
- [ ] Legal hold prevents all deletion

### Development Checklist:

#### Backend - Retention
- [ ] **Step 1**: Create RetentionPolicy model
  ```
  Location: backend/app/models/retention_policy.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `jurisdiction_id`: String(36), ForeignKey
    - `record_type`: String(50)
    - `retention_days`: Integer
    - `is_active`: Boolean

- [ ] **Step 2**: Create LegalHold model
  ```
  Location: backend/app/models/legal_hold.py
  ```
  - [ ] 2.1: Define model:
    - `id`: String(36), primary key
    - `target_type`: Enum (USER, CASE, RECORD)
    - `target_id`: String(36)
    - `reason`: Text
    - `created_by`: String(36)
    - `created_at`: DateTime
    - `released_at`: DateTime, nullable
    - `released_by`: String(36), nullable

- [ ] **Step 3**: Create RecordTombstone model
  - [ ] 3.1: Store: record_id, record_type, deleted_at, deletion_reason, hash_before_deletion

- [ ] **Step 4**: Create RetentionService
  - [ ] 4.1: Implement scheduled deletion job
  - [ ] 4.2: Check legal holds before deletion
  - [ ] 4.3: Perform cryptographic erasure
  - [ ] 4.4: Create tombstone record

---

# EPIC V2-18: Subpoena, Court Order & Legal Request Handling

## Objective
Standardize response to formal legal requests.

## User Story V2-18.1: Legal Request Intake

**As an** admin  
**I want** a portal for legal request intake  
**So that** we respond properly to subpoenas

### Acceptance Criteria:
- [ ] Admin-only intake portal
- [ ] Authority verification workflow
- [ ] Scoped export generation
- [ ] Disclosure audit logging

### Development Checklist:

#### Backend - Legal Request
- [ ] **Step 1**: Create LegalRequest model
  ```
  Location: backend/app/models/legal_request.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `request_type`: Enum (SUBPOENA, COURT_ORDER, AGENCY_REQUEST)
    - `requesting_authority`: String(255)
    - `authority_verified`: Boolean
    - `verified_by`: String(36), nullable
    - `scope`: JSON (date range, individuals, record types)
    - `received_at`: DateTime
    - `due_date`: Date
    - `status`: Enum (RECEIVED, VERIFIED, PROCESSING, COMPLETED, REJECTED)

- [ ] **Step 2**: Create LegalExportService
  - [ ] 2.1: Generate scoped exports
  - [ ] 2.2: Log all disclosures
  - [ ] 2.3: Prevent over-disclosure

---

# EPIC V2-19: Internal Staff Access Governance

## Objective
Demonstrate internal access boundaries.

## User Story V2-19.1: Least-Privilege Access

**As a** system  
**I want** role-based access with audit  
**So that** access is controlled and logged

### Acceptance Criteria:
- [ ] Least-privilege role definitions
- [ ] All access logged with justification
- [ ] Periodic access reviews

### Development Checklist:

#### Backend - Access Governance
- [ ] **Step 1**: Create Role and Permission models
- [ ] **Step 2**: Create StaffAccessLog model
- [ ] **Step 3**: Implement access review workflow

---

# EPIC V2-20: Temporal Integrity & Record Conflict Resolution

## Objective
Eliminate time-based disputes.

## User Story V2-20.1: UTC Timestamp Storage

**As a** system  
**I want** all timestamps in UTC with timezone metadata  
**So that** there are no time disputes

### Acceptance Criteria:
- [ ] UTC storage for all timestamps
- [ ] Timezone metadata stored separately
- [ ] DST transitions logged
- [ ] Device time drift detection
- [ ] Duplicate records allowed (both retained)

### Development Checklist:

#### Backend - Temporal Handling
- [ ] **Step 1**: Audit all timestamp columns
  - [ ] 1.1: Ensure all use `DateTime(timezone=True)`
  - [ ] 1.2: Add timezone metadata column where needed

- [ ] **Step 2**: Create TimeDriftService
  - [ ] 2.1: Detect device time drift
  - [ ] 2.2: Log significant drift as quality signal
  - [ ] 2.3: Flag for review if drift > 5 minutes

---

# EPIC V2-21: Professional Credential Lifecycle & Kill-Switch

## Objective
Ensure professional authority validation.

## User Story V2-21.1: Credential State Machine

**As a** system  
**I want** professional credentials managed with state machine  
**So that** only valid professionals can make decisions

### Acceptance Criteria:
- [ ] States: Active, Suspended, Revoked, Expired
- [ ] Periodic revalidation workflow
- [ ] Emergency suspension capability
- [ ] Kill-switch with justification logging

### Development Checklist:

#### Backend - Credential Management
- [ ] **Step 1**: Create ProfessionalCredential model
  ```
  Location: backend/app/models/professional_credential.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `professional_id`: String(36), ForeignKey
    - `credential_type`: String(100)
    - `credential_number`: String(100)
    - `state`: Enum (ACTIVE, SUSPENDED, REVOKED, EXPIRED)
    - `issued_at`: DateTime
    - `expires_at`: DateTime
    - `last_verified_at`: DateTime
    - `verification_source`: String(100)

- [ ] **Step 2**: Create KillSwitchLog model
  - [ ] 2.1: Log all activations with justification

---

# EPIC V2-22: Individual Subscriptions & Billing (Stripe)

## Objective
Implement subscription billing for ad-free tier.

## User Story V2-22.1: Stripe Subscription Integration

**As a** user  
**I want to** subscribe for ad-free experience  
**So that** I can use the app without ads

### Acceptance Criteria:
- [ ] Stripe as exclusive payment processor
- [ ] Ad-free subscription tier
- [ ] Billing lifecycle webhooks
- [ ] No payment-based compliance advantages
- [ ] Documentation features identical for free/paid

### Development Checklist:

#### Backend - Stripe Integration
- [ ] **Step 1**: Create Subscription model
  ```
  Location: backend/app/models/subscription.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `contact_id`: String(36), ForeignKey
    - `stripe_customer_id`: String(100)
    - `stripe_subscription_id`: String(100)
    - `plan`: Enum (FREE, AD_FREE)
    - `status`: Enum (ACTIVE, CANCELLED, PAST_DUE)
    - `current_period_start`: DateTime
    - `current_period_end`: DateTime

- [ ] **Step 2**: Create StripeWebhookService
  - [ ] 2.1: Handle subscription.created
  - [ ] 2.2: Handle subscription.updated
  - [ ] 2.3: Handle subscription.deleted
  - [ ] 2.4: Handle payment_failed

- [ ] **Step 3**: Create payment API endpoints
  - [ ] 3.1: `POST /api/v1/subscriptions/create-checkout-session`
  - [ ] 3.2: `POST /api/v1/subscriptions/webhook` - Stripe webhook
  - [ ] 3.3: `GET /api/v1/subscriptions/status`
  - [ ] 3.4: `POST /api/v1/subscriptions/cancel`

---

# EPIC V2-23: Verification Provider Framework

## Objective
Create swappable verification layer for timestamp and integrity anchoring.

## User Story V2-23.1: Provider Interface

**As a** system  
**I want** pluggable verification providers  
**So that** we can upgrade from native to third-party to blockchain

### Acceptance Criteria:
- [ ] Unified provider interface
- [ ] Providers: VC_NATIVE, THIRD_PARTY, BLOCKCHAIN
- [ ] Every evidentiary event produces verification proof
- [ ] Switching providers requires no feature code changes
- [ ] Proof failures don't block operations

### Development Checklist:

#### Backend - Verification Framework
- [ ] **Step 1**: Create VerificationProof model
  ```
  Location: backend/app/models/verification_proof.py
  ```
  - [ ] 1.1: Define model:
    - `id`: String(36), primary key
    - `event_type`: String(50) (CHECKIN, CHECKOUT, REPORT_ISSUED, MSG_EXPORT)
    - `event_id`: String(36)
    - `provider`: Enum (VC_NATIVE, THIRD_PARTY, BLOCKCHAIN)
    - `payload_hash`: String(64)
    - `occurred_at`: DateTime
    - `proof_blob`: JSON (provider-specific token/receipt/tx ref)
    - `status`: Enum (CREATED, PENDING, VERIFIED, FAILED)
    - `provider_key_version`: String(20)
    - `created_at`: DateTime
    - `verified_at`: DateTime, nullable

- [ ] **Step 2**: Create VerificationProvider interface
  ```
  Location: backend/app/services/verification/base.py
  ```
  - [ ] 2.1: Define abstract base class:
    ```python
    class VerificationProvider(ABC):
        @abstractmethod
        async def create_proof(self, payload_hash, event_type, event_id, occurred_at): pass
        
        @abstractmethod
        async def verify_proof(self, proof_record): pass
        
        @abstractmethod
        def provider_metadata(self): pass
    ```

- [ ] **Step 3**: Implement VC_NATIVE provider
  ```
  Location: backend/app/services/verification/vc_native.py
  ```
  - [ ] 3.1: Generate server-side signature
  - [ ] 3.2: Store proof record
  - [ ] 3.3: Implement verification

- [ ] **Step 4**: Create placeholder for THIRD_PARTY provider
  - [ ] 4.1: Interface adapter for TSA/notary service
  - [ ] 4.2: Async proof retrieval

- [ ] **Step 5**: Create placeholder for BLOCKCHAIN provider
  - [ ] 5.1: Merkle root batching logic
  - [ ] 5.2: Transaction reference storage

- [ ] **Step 6**: Create VerificationService
  ```
  Location: backend/app/services/verification_service.py
  ```
  - [ ] 6.1: Get active provider from config
  - [ ] 6.2: Create proofs at hook points:
    - Check-in finalized
    - Check-out finalized
    - VC report finalized
    - Message export finalized
  - [ ] 6.3: Async retry for failed proofs
  - [ ] 6.4: Feature flag for dual proofs during transition

- [ ] **Step 7**: Display proof status in UI
  - [ ] 7.1: Show in QR report viewer
  - [ ] 7.2: Show in message export metadata
  - [ ] 7.3: Include provider name, status, timestamp, reference

---

# MIGRATION & DEPLOYMENT PLAN

## Database Migrations (Recommended Order)

1. **Phase 1 - Core Models** (Week 1-2)
   - consent_artifacts
   - verification_codes
   - user_identities
   - jurisdictions
   - policy_versions

2. **Phase 2 - Mandate System** (Week 3-4)
   - mandates
   - enrollment_tokens
   - sms_delivery_logs

3. **Phase 3 - Enhanced Documentation** (Week 5-6)
   - selfie_artifacts
   - data_quality_signals
   - emergency_explanations
   - explanation_attachments

4. **Phase 4 - Review & Messaging** (Week 7-8)
   - review_artifacts
   - message_threads
   - messages
   - message_attachments
   - sla_tracking

5. **Phase 5 - Reports & Verification** (Week 9-10)
   - report_templates
   - vc_reports
   - verification_proofs
   - audit_entries

6. **Phase 6 - Governance & Billing** (Week 11-12)
   - legal_holds
   - record_tombstones
   - legal_requests
   - professional_credentials
   - subscriptions

---

# TESTING REQUIREMENTS

## Unit Tests (>80% Coverage)
- All service layer methods
- All model methods
- API endpoint validation
- Policy engine logic

## Integration Tests
- Full check-in/check-out flow
- Mandate enrollment flow
- Message export flow
- Verification proof generation

## End-to-End Tests
- Complete user journey
- Professional review workflow
- Billing subscription flow

---

# DEFINITION OF DONE (Per User Story)

A user story is "done" when:
- [ ] Code written following architecture patterns
- [ ] Database migration created and tested
- [ ] API endpoints documented in OpenAPI
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Accessibility requirements met
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Code reviewed and merged
- [ ] Deployed to staging
- [ ] UAT completed

---

**END OF ENHANCED REQUIREMENTS DOCUMENT**

Total New Epics: 23  
Total New User Stories: 50+  
Estimated Additional Timeline: 12-16 weeks (3 developers)

