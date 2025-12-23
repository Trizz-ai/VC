# Verified Compliance™ — Project Handoff Documentation

## Welcome, New Developer!

This document serves as your entry point to the Verified Compliance codebase. Read this first, then proceed to the specialized documents based on your needs.

---

## 📁 Documentation Index

| Document | Audience | Purpose |
|----------|----------|---------|
| `HANDOFF_README.md` | Everyone | You're reading it - start here |
| `HANDOFF_TECHNICAL.md` | Developers | Deep technical architecture, patterns, and code walkthrough |
| `HANDOFF_CLIENT.md` | Stakeholders | Business context, feature status, and roadmap |
| `HANDOFF_SETUP_GUIDE.md` | Developers | Step-by-step local development setup |
| `HANDOFF_API_REFERENCE.md` | Developers | Complete API documentation |
| `HANDOFF_DATABASE_SCHEMA.md` | Developers | Database models, relationships, and migrations |
| `HANDOFF_DEPLOYMENT.md` | DevOps | Deployment procedures and infrastructure |
| `HANDOFF_TESTING.md` | QA/Developers | Testing strategy and how to run tests |
| `epics.md` | Everyone | Original product requirements |
| `epics_v2_enhanced_requirements.md` | Everyone | New enhanced requirements |
| `DEVELOPMENT_CHECKLIST_V2.md` | Developers | Granular implementation checklists |
| `EPICS_SUMMARY_MATRIX.md` | Everyone | Priority matrix and delivery timeline |

---

## 🎯 Project Overview

### What is Verified Compliance?

Verified Compliance is a **mobile documentation platform** (Flutter + FastAPI) that enables individuals to record their attendance at meetings, events, or custom locations with GPS and biometric verification. 

**Critical Distinction:** This is a **documentation tool**, NOT an automated compliance verification system. All compliance determinations are made by supervising professionals, not the software.

### Core User Personas

1. **Individuals** - People who need to document their attendance (mobile app)
2. **Professionals** - Supervisors who review documentation and make determinations (web portal)
3. **Administrators** - System administrators who manage meetings, policies, and users

### Key Features (Current)

- ✅ User registration with consent capture
- ✅ GPS-verified check-in/check-out
- ✅ Meeting discovery (nearby + search)
- ✅ Session history and activity logs
- ✅ GoHighLevel CRM integration
- ✅ Offline queue with sync
- ✅ Admin dashboard
- ✅ AI assistant (basic)

### Key Features (Planned - See epics_v2)

- 🔲 Mandatory 2FA before first check-in
- 🔲 Professional mandate creation via SMS
- 🔲 Biometric selfie capture with liveness detection
- 🔲 Immutable record storage with audit chain
- 🔲 Professional review queue
- 🔲 In-app messaging with export
- 🔲 Server-side report generation with QR verification
- 🔲 Stripe subscription billing

---

## 🏗️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.104+ | Web framework |
| SQLAlchemy | 2.0+ | ORM (async) |
| Alembic | Latest | Database migrations |
| Pydantic | 2.0+ | Data validation |
| PostgreSQL | 15+ | Production database |
| SQLite | - | Development database |
| Redis | 7+ | Caching (optional) |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flutter | 3.16+ | Cross-platform framework |
| Dart | 3.0+ | Programming language |
| Provider | Latest | State management |
| Geolocator | Latest | GPS services |
| HTTP | Latest | API communication |
| SQLite | Latest | Local storage |

### Infrastructure
| Service | Purpose |
|---------|---------|
| Fly.io | Backend hosting |
| Neon/Supabase | Managed PostgreSQL |
| GitHub Actions | CI/CD |
| Sentry | Error tracking |

---

## 📂 Repository Structure

```
X:\VC\
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API route handlers
│   │   ├── core/              # Configuration, auth, database
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── pyproject.toml         # Dependencies
│
├── frontend/                   # Flutter mobile app
│   ├── lib/
│   │   ├── app/               # App configuration, routing
│   │   ├── core/              # Shared utilities, services
│   │   ├── features/          # Feature modules (auth, sessions, etc.)
│   │   └── ui/                # Screens and widgets
│   ├── test/                  # Frontend tests
│   └── pubspec.yaml           # Dependencies
│
├── docs/                       # Additional documentation
├── screens/                    # Screenshots
└── *.md                        # Documentation files
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- Flutter 3.16+
- Git

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install poetry
poetry install
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
flutter pub get
flutter run -d chrome  # Web
flutter run            # Mobile emulator
```

**Detailed setup instructions:** See `HANDOFF_SETUP_GUIDE.md`

---

## 🔑 Key Contacts & Resources

### Original Development Team
- Handoff Date: December 2024
- Documentation Version: 2.0

### External Services
| Service | Purpose | Credentials Location |
|---------|---------|---------------------|
| GoHighLevel | CRM integration | `.env` file |
| Google Maps | Geocoding | `.env` file |
| Twilio (planned) | SMS delivery | `.env` file |
| Stripe (planned) | Payments | `.env` file |
| Sentry | Error tracking | `.env` file |

### Useful Links
- GoHighLevel API Docs: https://highlevel.stoplight.io/
- Flutter Docs: https://docs.flutter.dev/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

## ⚠️ Critical Information

### Absolute Development Rules

These rules are **non-negotiable** and must be followed:

1. **Single-line imports only** - No multi-line imports, no relative imports
   ```python
   # ✅ CORRECT
   import fastapi
   import sqlalchemy
   
   # ❌ WRONG
   from app.models import (
       Contact,
       Session,
   )
   ```

2. **No mocks in tests** - All tests must use real implementations with real data

3. **Terminology enforcement** - Never use "verified", "proven", "confirmed", "compliance score", or "pass/fail" in user-facing text. This is a DOCUMENTATION tool.

4. **Records are immutable** - Once submitted, records cannot be modified. All changes are new records.

5. **UTC timestamps** - All timestamps stored in UTC with timezone metadata

### Known Issues / Technical Debt

1. Some test files still have mock implementations - need refactoring
2. Frontend has some unused imports to clean up
3. Error handling could be more consistent across services
4. Some API responses don't include the disclaimer text yet

---

## 📋 What's Next?

1. **Read** `HANDOFF_SETUP_GUIDE.md` to get your local environment running
2. **Read** `HANDOFF_TECHNICAL.md` for architecture deep-dive
3. **Review** `epics_v2_enhanced_requirements.md` for upcoming features
4. **Follow** `DEVELOPMENT_CHECKLIST_V2.md` for implementation guidance

---

## 🆘 Getting Help

If you're stuck:

1. Check the documentation files listed above
2. Search the codebase for similar implementations
3. Review existing tests for usage examples
4. Check the API docs at `/docs` when backend is running

---

**Good luck! This is a well-structured codebase with clear patterns. Once you understand the architecture, adding features should be straightforward.**

