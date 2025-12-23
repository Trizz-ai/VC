# Verified Compliance - System Architecture

## ABSOLUTE DESIGN RULES - NO EXCEPTIONS
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

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Data Flow Architecture](#data-flow-architecture)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Integration Architecture](#integration-architecture)
9. [Performance Architecture](#performance-architecture)
10. [Monitoring & Observability](#monitoring--observability)
11. [Scalability Patterns](#scalability-patterns)
12. [Design Patterns](#design-patterns)
13. [Microservices Architecture](#microservices-architecture)
14. [Event-Driven Architecture](#event-driven-architecture)
15. [Caching Architecture](#caching-architecture)
16. [Database Architecture](#database-architecture)
17. [API Architecture](#api-architecture)
18. [Mobile Architecture](#mobile-architecture)
19. [DevOps Architecture](#devops-architecture)
20. [Compliance & Security](#compliance--security)

---

## System Overview

### Application Purpose
Verified Compliance is a mobile attendance tracking system that enables users to log their presence at meetings, events, or custom destinations with GPS verification. The system integrates with GoHighLevel CRM for contact management and provides public shareable logs for verification purposes.

### Core Features
- **GPS-Verified Check-In/Check-Out**: Users can check in and out of locations with GPS verification
- **Meeting Discovery**: Find nearby meetings or create custom destinations
- **Activity Logs**: View, search, and filter attendance history
- **Public Sharing**: Generate shareable links for verification
- **CRM Integration**: Automatic sync with GoHighLevel
- **Offline Support**: Queue actions when offline, sync when online

### Key Constraints
- **Privacy First**: GPS only captured during explicit check-in/out actions
- **Security**: All data encrypted in transit and at rest
- **Performance**: Sub-300ms API response times
- **Reliability**: 99.9% uptime target
- **Compliance**: GDPR-ready data handling

---

## Architecture Principles

### 1. Microservices-Ready Monolith
- **Current**: Single FastAPI application with clear module boundaries
- **Future**: Easy to extract services (auth, sessions, notifications)
- **Benefits**: Simple deployment, clear ownership, easy testing

### 2. API-First Design
- **RESTful APIs**: Standard HTTP methods and status codes
- **OpenAPI Specification**: Auto-generated documentation
- **Versioning**: `/api/v1/` prefix for future compatibility
- **Benefits**: Clear contracts, easy testing, frontend flexibility

### 3. Mobile-First Backend
- **Optimized for Mobile**: Lightweight responses, efficient data structures
- **Offline Support**: Queue-based architecture for offline operations
- **Real-time Updates**: WebSocket support for live session updates
- **Benefits**: Better mobile experience, reduced data usage

### 4. Event-Driven Architecture
- **Domain Events**: Session created, checked in, checked out
- **Event Sourcing**: Audit trail for all user actions
- **Async Processing**: Background tasks for CRM sync, notifications
- **Benefits**: Scalability, auditability, loose coupling

### 5. Security by Design
- **Zero Trust**: Every request authenticated and authorized
- **Data Minimization**: Collect only necessary information
- **Encryption**: All sensitive data encrypted at rest and in transit
- **Benefits**: Compliance, user trust, reduced risk

---

## Technology Stack

### Backend (Python)
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  API Layer     │  Business Logic  │  Data Access  │  Utils   │
│  - Routes      │  - Services      │  - Models     │  - Auth  │
│  - Schemas     │  - Validators    │  - Repos      │  - Crypto│
│  - Middleware  │  - Events        │  - Migrations │  - Geo   │
└─────────────────────────────────────────────────────────────┘
```

**Core Technologies:**
- **FastAPI 0.104+**: Modern, fast web framework with automatic OpenAPI docs
- **Python 3.11+**: Latest stable Python with performance improvements
- **SQLAlchemy 2.0+**: Modern ORM with async support
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

**Database & Storage:**
- **PostgreSQL 15+**: Primary database with ACID compliance
- **PostGIS Extension**: Geospatial queries for location-based features
- **Redis**: Caching and session storage
- **AWS S3**: File storage for QR codes and exports

**Authentication & Security:**
- **JWT Tokens**: Stateless authentication
- **Bcrypt**: Password hashing
- **HMAC-SHA256**: Webhook signature verification
- **HTTPS/TLS**: Transport security

### Frontend (Flutter)
```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Application                      │
├─────────────────────────────────────────────────────────────┤
│  UI Layer      │  State Mgmt    │  Services     │  Utils    │
│  - Screens      │  - Providers   │  - API Client │  - Auth  │
│  - Widgets     │  - Models      │  - Storage    │  - Geo   │
│  - Navigation  │  - Events      │  - Cache      │  - Utils  │
└─────────────────────────────────────────────────────────────┘
```

**Core Technologies:**
- **Flutter 3.16+**: Cross-platform mobile framework
- **Dart 3.0+**: Type-safe programming language
- **Provider/Riverpod**: State management
- **HTTP/Dio**: API communication
- **SQLite**: Local data storage

**Key Packages:**
- **geolocator**: GPS location services
- **permission_handler**: Runtime permissions
- **connectivity_plus**: Network status detection
- **flutter_secure_storage**: Secure credential storage
- **sqflite**: Local database
- **qr_flutter**: QR code generation
- **cached_network_image**: Image caching

### Infrastructure
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Infrastructure                     │
├─────────────────────────────────────────────────────────────┤
│  CDN/Edge      │  Application   │  Database    │  Storage   │
│  - CloudFlare  │  - Fly.io      │  - Neon      │  - AWS S3  │
│  - Caching     │  - Docker      │  - Postgres  │  - Files   │
│  - SSL/TLS     │  - Auto-scale  │  - PostGIS   │  - Backups │
└─────────────────────────────────────────────────────────────┘
```

**Hosting & Deployment:**
- **Fly.io**: Container hosting with global edge deployment
- **Docker**: Containerization for consistent deployments
- **GitHub Actions**: CI/CD pipeline automation
- **Neon/Supabase**: Managed PostgreSQL with PostGIS

**Monitoring & Observability:**
- **Sentry**: Error tracking and performance monitoring
- **Logtail**: Centralized logging
- **UptimeRobot**: Uptime monitoring
- **Grafana**: Metrics visualization

---

## System Components

### Backend Components

#### 1. API Layer (`app/api/`)
```
api/
├── v1/
│   ├── auth.py          # Authentication endpoints
│   ├── contacts.py   # Contact management
│   ├── meetings.py     # Meeting discovery
│   ├── sessions.py     # Session lifecycle
│   ├── exports.py      # Data export
│   └── admin.py        # Administrative functions
├── middleware/
│   ├── auth.py         # JWT validation
│   ├── rate_limit.py   # Rate limiting
│   └── cors.py         # CORS handling
└── dependencies.py     # Shared dependencies
```

**Responsibilities:**
- HTTP request/response handling
- Input validation using Pydantic schemas
- Authentication and authorization
- Rate limiting and security headers
- API versioning and documentation

#### 2. Business Logic Layer (`app/services/`)
```
services/
├── auth_service.py     # Authentication logic
├── contact_service.py  # Contact management
├── session_service.py  # Session lifecycle
├── meeting_service.py  # Meeting discovery
├── ghl_service.py      # CRM integration
├── export_service.py   # Data export
└── notification_service.py # Notifications
```

**Responsibilities:**
- Business rule enforcement
- Data transformation
- External API integration
- Event publishing
- Error handling and logging

#### 3. Data Access Layer (`app/models/`)
```
models/
├── base.py             # Base model class
├── contact.py          # Contact entity
├── meeting.py          # Meeting entity
├── session.py          # Session entity
├── session_event.py    # Event entity
├── public_share.py     # Share entity
├── webhook_log.py      # Audit entity
└── qr_campaign.py      # Campaign entity
```

**Responsibilities:**
- Database schema definition
- Relationship mapping
- Data validation
- Query optimization
- Migration management

#### 4. Utility Layer (`app/utils/`)
```
utils/
├── auth.py             # JWT utilities
├── crypto.py           # Encryption/hashing
├── geo.py              # Geospatial calculations
├── ghl_client.py       # GHL API client
├── email_client.py     # Email service
└── validators.py       # Custom validators
```

**Responsibilities:**
- Reusable utility functions
- External service clients
- Data transformation helpers
- Security utilities

### Frontend Components

#### 1. Presentation Layer (`lib/screens/`)
```
screens/
├── onboarding/
│   ├── consent_screen.dart
│   └── contact_form_screen.dart
├── discovery/
│   ├── meeting_finder_screen.dart
│   └── custom_destination_screen.dart
├── session/
│   ├── session_screen.dart
│   └── check_in_out_screen.dart
├── dashboard/
│   ├── activity_logs_screen.dart
│   └── log_details_screen.dart
├── share/
│   └── public_share_screen.dart
└── settings/
    └── settings_screen.dart
```

#### 2. State Management (`lib/providers/`)
```
providers/
├── auth_provider.dart      # Authentication state
├── session_provider.dart   # Session management
├── meeting_provider.dart   # Meeting data
├── location_provider.dart  # GPS services
└── export_provider.dart   # Export functionality
```

#### 3. Service Layer (`lib/services/`)
```
services/
├── api_service.dart        # HTTP client
├── storage_service.dart    # Local storage
├── location_service.dart   # GPS services
├── notification_service.dart # Push notifications
└── sync_service.dart      # Offline sync
```

#### 4. Widget Library (`lib/widgets/`)
```
widgets/
├── common/
│   ├── loading_widget.dart
│   ├── error_widget.dart
│   └── empty_state_widget.dart
├── forms/
│   ├── contact_form.dart
│   └── notes_form.dart
├── lists/
│   ├── meeting_list.dart
│   └── log_list.dart
└── maps/
    └── location_map.dart
```

---

## Data Flow Architecture

### 1. User Onboarding Flow
```
User → Flutter App → API Gateway → Auth Service → Database
  ↓
Contact Created → GHL Sync → JWT Token → Local Storage
```

**Sequence:**
1. User opens app for first time
2. Consent screen with GPS permission request
3. Contact form submission
4. Backend creates contact record
5. GHL contact upsert via API
6. JWT token generation
7. Token stored in Flutter secure storage

### 2. Session Lifecycle Flow
```
User Action → GPS Capture → API Validation → Database Update → GHL Sync
     ↓              ↓              ↓              ↓
  Check-In → Location Verify → Session Update → Webhook Send
     ↓              ↓              ↓              ↓
  Check-Out → Duration Calc → Final Update → CRM Update
```

**Sequence:**
1. User selects meeting or custom destination
2. Session created with 15-minute expiration
3. Check-in with GPS verification (200m threshold)
4. Session notes (optional)
5. Check-out with GPS verification
6. Duration calculation and session completion
7. GHL webhook with full session data

### 3. Offline Sync Flow
```
Offline Action → Local Storage → Queue → Network Check → API Sync
      ↓              ↓              ↓              ↓
   Check-In → SQLite Store → Background → Online → Batch Send
```

**Sequence:**
1. User performs action while offline
2. Data stored in local SQLite database
3. Background service monitors connectivity
4. When online, queued actions sent to API
5. Success confirmation and local cleanup

### 4. Data Export Flow
```
User Request → Selection → API Call → PDF Generation → Email Send
     ↓              ↓              ↓              ↓
  Log Selection → Filter Apply → Backend Process → Email Delivery
```

**Sequence:**
1. User selects logs for export
2. Filter options applied (date range, category)
3. API generates PDF with selected data
4. Email sent via SMTP or GHL workflow
5. Success confirmation to user

---

## Security Architecture

### 1. Authentication & Authorization
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│  Transport    │  Application  │  Data       │  Storage     │
│  - HTTPS/TLS  │  - JWT Auth   │  - Encryption│  - Encrypted │
│  - HSTS       │  - Rate Limit │  - Hashing   │  - Access     │
│  - CORS       │  - Validation │  - Signing   │  - Backup     │
└─────────────────────────────────────────────────────────────┘
```

**Authentication Flow:**
1. User submits contact information
2. Backend validates and creates contact
3. JWT token generated with 15-minute expiration
4. Token stored in Flutter secure storage
5. All API calls include Bearer token
6. Token validated on each request

**Authorization Rules:**
- Users can only access their own sessions
- Admin endpoints require special tokens
- Public share pages require valid tokens
- Rate limiting: 100 requests/minute per IP

### 2. Data Protection
```
┌─────────────────────────────────────────────────────────────┐
│                    Data Protection                         │
├─────────────────────────────────────────────────────────────┤
│  In Transit   │  At Rest     │  Processing  │  Sharing     │
│  - TLS 1.3    │  - AES-256  │  - Memory    │  - Tokens    │
│  - Certificate│  - Database  │  - Secure    │  - Expiry    │
│  - Pinning    │  - Files     │  - Clearing  │  - Revoke    │
└─────────────────────────────────────────────────────────────┘
```

**Encryption Standards:**
- **Transport**: TLS 1.3 with perfect forward secrecy
- **Database**: AES-256 encryption at rest
- **Files**: S3 server-side encryption
- **Secrets**: Environment variables with rotation

### 3. Privacy Controls
```
┌─────────────────────────────────────────────────────────────┐
│                    Privacy Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Collection   │  Processing  │  Storage     │  Sharing      │
│  - Minimal    │  - Purpose   │  - Retention │  - Consent    │
│  - Consent    │  - Lawful    │  - Secure    │  - Control    │
│  - Transparent│  - Fair      │  - Access    │  - Revoke     │
└─────────────────────────────────────────────────────────────┘
```

**Privacy Principles:**
- **Data Minimization**: Collect only necessary information
- **Purpose Limitation**: Use data only for stated purposes
- **Consent**: Explicit consent for GPS tracking
- **Transparency**: Clear privacy policy and data usage
- **Control**: User can request data deletion

---

## Deployment Architecture

### 1. Production Environment
```
┌─────────────────────────────────────────────────────────────┐
│                    Production Stack                       │
├─────────────────────────────────────────────────────────────┤
│  CDN/Edge     │  Application │  Database   │  Monitoring   │
│  - CloudFlare │  - Fly.io    │  - Neon     │  - Sentry     │
│  - Global     │  - Docker    │  - Postgres │  - Logtail    │
│  - SSL        │  - Auto-scale│  - PostGIS  │  - Uptime     │
└─────────────────────────────────────────────────────────────┘
```

**Infrastructure Components:**
- **CDN**: CloudFlare for global content delivery
- **Application**: Fly.io with Docker containers
- **Database**: Neon PostgreSQL with PostGIS
- **Storage**: AWS S3 for files and backups
- **Monitoring**: Sentry, Logtail, UptimeRobot

### 2. Development Environment
```
┌─────────────────────────────────────────────────────────────┐
│                    Development Stack                       │
├─────────────────────────────────────────────────────────────┤
│  Local        │  Staging     │  Testing    │  CI/CD        │
│  - Docker     │  - Fly.io    │  - GitHub   │  - Actions   │
│  - Postgres   │  - Staging   │  - Tests    │  - Deploy    │
│  - Redis      │  - Database  │  - Coverage │  - Notify    │
└─────────────────────────────────────────────────────────────┘
```

**Development Workflow:**
1. **Local Development**: Docker Compose with all services
2. **Staging Environment**: Identical to production
3. **Testing**: Automated tests in CI/CD pipeline
4. **Deployment**: Automated deployment on merge to main

### 3. CI/CD Pipeline
```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│  Trigger      │  Build       │  Test       │  Deploy       │
│  - Push       │  - Docker    │  - Unit     │  - Staging    │
│  - PR         │  - Image     │  - Integration│  - Production│
│  - Tag        │  - Registry  │  - E2E      │  - Notify     │
└─────────────────────────────────────────────────────────────┘
```

**Pipeline Stages:**
1. **Trigger**: Push to main branch or PR creation
2. **Build**: Docker image creation and registry push
3. **Test**: Unit tests, integration tests, security scans
4. **Deploy**: Staging deployment, smoke tests, production deployment
5. **Notify**: Slack notifications for success/failure

---

## Integration Architecture

### 1. GoHighLevel Integration
```
┌─────────────────────────────────────────────────────────────┐
│                    GHL Integration                         │
├─────────────────────────────────────────────────────────────┤
│  Contact      │  Custom      │  Tags        │  Webhooks    │
│  - Upsert     │  - Fields    │  - Add/Remove│  - Payload   │
│  - Search     │  - Update    │  - Workflows │  - Signature │
│  - Validate   │  - Sync      │  - Triggers  │  - Retry     │
└─────────────────────────────────────────────────────────────┘
```

**Integration Points:**
- **Contact Management**: Automatic upsert on contact creation
- **Custom Fields**: Session data sync to GHL fields
- **Tags**: Automatic tagging based on session events
- **Webhooks**: Real-time data delivery to GHL workflows

### 2. Google Maps Integration
```
┌─────────────────────────────────────────────────────────────┐
│                    Maps Integration                        │
├─────────────────────────────────────────────────────────────┤
│  Geocoding    │  Static Maps │  Distance    │  Places      │
│  - Address    │  - Images    │  - Matrix    │  - Search    │
│  - Lat/Lng    │  - Share     │  - Routes    │  - Details   │
│  - Validation │  - Cache     │  - ETA       │  - Reviews   │
└─────────────────────────────────────────────────────────────┘
```

**Maps Services:**
- **Geocoding**: Convert addresses to coordinates
- **Static Maps**: Generate map images for sharing
- **Distance Matrix**: Calculate travel times
- **Places API**: Find nearby locations

### 3. Email Integration
```
┌─────────────────────────────────────────────────────────────┐
│                    Email Integration                        │
├─────────────────────────────────────────────────────────────┤
│  SMTP         │  SendGrid    │  Templates   │  Tracking    │
│  - Direct     │  - API       │  - HTML      │  - Opens     │
│  - Auth       │  - Webhooks  │  - Text      │  - Clicks    │
│  - TLS        │  - Analytics │  - Variables│  - Bounces    │
└─────────────────────────────────────────────────────────────┘
```

**Email Services:**
- **SMTP**: Direct email sending for exports
- **SendGrid**: Transactional email service
- **Templates**: HTML email templates for exports
- **Tracking**: Delivery and engagement tracking

---

## Performance Architecture

### 1. Backend Performance
```
┌─────────────────────────────────────────────────────────────┐
│                    Performance Layers                      │
├─────────────────────────────────────────────────────────────┤
│  CDN         │  Application │  Database    │  Caching      │
│  - Static    │  - Async     │  - Indexes   │  - Redis      │
│  - Global    │  - Pool      │  - Queries   │  - Memory     │
│  - Cache     │  - Workers   │  - Connection│  - TTL        │
└─────────────────────────────────────────────────────────────┘
```

**Performance Targets:**
- **API Response Time**: 95th percentile < 300ms
- **Database Queries**: < 100ms for simple queries
- **Cache Hit Rate**: > 90% for meeting data
- **Concurrent Users**: 1000+ simultaneous users

### 2. Database Optimization
```
┌─────────────────────────────────────────────────────────────┐
│                    Database Performance                    │
├─────────────────────────────────────────────────────────────┤
│  Indexes      │  Queries     │  Connection  │  Monitoring  │
│  - Primary    │  - Optimized │  - Pooling   │  - Slow      │
│  - Foreign    │  - Cached    │  - Limits    │  - Metrics   │
│  - Spatial    │  - Paginated │  - Timeout   │  - Alerts    │
└─────────────────────────────────────────────────────────────┘
```

**Database Indexes:**
- **Contacts**: email, phone, ghl_contact_id
- **Meetings**: lat, lng (spatial), category, active
- **Sessions**: contact_id, created_at, status
- **Events**: session_id, type, timestamp

### 3. Caching Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    Caching Architecture                    │
├─────────────────────────────────────────────────────────────┤
│  Application │  Database    │  CDN         │  Browser     │
│  - Redis     │  - Query     │  - Static    │  - Local     │
│  - Memory    │  - Result    │  - Images    │  - Storage   │
│  - TTL       │  - Cache     │  - API       │  - Cache     │
└─────────────────────────────────────────────────────────────┘
```

**Caching Layers:**
- **Application**: Redis for session data and API responses
- **Database**: Query result caching for expensive operations
- **CDN**: Static assets and API responses
- **Browser**: Local storage for user preferences

---

## Monitoring & Observability

### 1. Application Monitoring
```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                        │
├─────────────────────────────────────────────────────────────┤
│  Errors      │  Performance │  Logs        │  Metrics      │
│  - Sentry    │  - APM       │  - Logtail   │  - Custom     │
│  - Alerts    │  - Traces    │  - Structured│  - Business   │
│  - Context   │  - Profiling │  - Search    │  - Technical  │
└─────────────────────────────────────────────────────────────┘
```

**Monitoring Components:**
- **Error Tracking**: Sentry for exception monitoring
- **Performance**: Application performance monitoring
- **Logging**: Structured logging with Logtail
- **Metrics**: Custom business and technical metrics

### 2. Infrastructure Monitoring
```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Monitoring               │
├─────────────────────────────────────────────────────────────┤
│  Uptime      │  Resources   │  Database    │  Security    │
│  - Ping      │  - CPU       │  - Queries   │  - Scans      │
│  - Health    │  - Memory    │  - Connections│  - Alerts    │
│  - Alerts    │  - Disk      │  - Locks     │  - Logs      │
└─────────────────────────────────────────────────────────────┘
```

**Infrastructure Monitoring:**
- **Uptime**: UptimeRobot for availability monitoring
- **Resources**: CPU, memory, disk usage tracking
- **Database**: Query performance and connection monitoring
- **Security**: Vulnerability scanning and alerting

### 3. Business Metrics
```
┌─────────────────────────────────────────────────────────────┐
│                    Business Metrics                        │
├─────────────────────────────────────────────────────────────┤
│  Users       │  Sessions    │  Performance │  Quality      │
│  - Active    │  - Created   │  - Response  │  - Errors     │
│  - New       │  - Completed │  - Time      │  - Success    │
│  - Retention │  - Duration  │  - Throughput│  - Rate      │
└─────────────────────────────────────────────────────────────┘
```

**Key Metrics:**
- **User Metrics**: Daily active users, new registrations
- **Session Metrics**: Sessions created, completion rate
- **Performance Metrics**: API response times, error rates
- **Quality Metrics**: GPS accuracy, location verification success

---

## Scalability Considerations

### 1. Horizontal Scaling
- **Application**: Stateless FastAPI instances behind load balancer
- **Database**: Read replicas for query distribution
- **Caching**: Redis cluster for high availability
- **Storage**: S3 with CDN for global content delivery

### 2. Vertical Scaling
- **Application**: Multi-core processing with async/await
- **Database**: Connection pooling and query optimization
- **Memory**: Efficient data structures and caching
- **Storage**: SSD storage for database performance

### 3. Future Enhancements
- **Microservices**: Extract auth, sessions, notifications
- **Event Streaming**: Apache Kafka for real-time events
- **Machine Learning**: Location accuracy improvements
- **Mobile SDK**: Native iOS/Android SDKs

---

## Disaster Recovery

### 1. Backup Strategy
- **Database**: Daily automated backups with point-in-time recovery
- **Files**: S3 versioning and cross-region replication
- **Code**: Git repository with multiple remotes
- **Configuration**: Infrastructure as code with version control

### 2. Recovery Procedures
- **RTO**: Recovery Time Objective < 1 hour
- **RPO**: Recovery Point Objective < 15 minutes
- **Testing**: Monthly disaster recovery drills
- **Documentation**: Step-by-step recovery procedures

### 3. High Availability
- **Multi-Region**: Primary and secondary regions
- **Load Balancing**: Health checks and failover
- **Database**: Master-slave replication
- **Monitoring**: Automated failover detection

---

## Compliance & Security

### 1. Data Protection
- **Encryption**: AES-256 for data at rest, TLS 1.3 for transit
- **Access Control**: Role-based access with principle of least privilege
- **Audit Logging**: All data access and modifications logged
- **Data Retention**: Configurable retention policies

### 2. Privacy Compliance
- **GDPR**: Right to access, rectification, erasure
- **CCPA**: Data subject rights and opt-out mechanisms
- **Consent Management**: Granular consent tracking
- **Data Minimization**: Collect only necessary information

### 3. Security Controls
- **Authentication**: Multi-factor authentication for admin access
- **Authorization**: Fine-grained permissions
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: DDoS protection and abuse prevention

---

## Scalability Patterns

### 1. Horizontal Scaling Patterns

#### Load Balancing Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancing Architecture              │
├─────────────────────────────────────────────────────────────┤
│  CDN/Edge     │  Load Balancer │  Application │  Database   │
│  - CloudFlare │  - Round Robin │  - Multiple  │  - Master   │
│  - Global     │  - Health Check │  - Instances │  - Replicas │
│  - Caching    │  - Failover    │  - Stateless │  - Sharding  │
└─────────────────────────────────────────────────────────────┘
```

**Scaling Strategies:**
- **CDN Layer**: CloudFlare for global content delivery and caching
- **Load Balancer**: Round-robin with health checks and failover
- **Application Layer**: Multiple stateless FastAPI instances
- **Database Layer**: Master-slave replication with read replicas

#### Auto-Scaling Configuration
```yaml
# Fly.io auto-scaling configuration
app:
  name: verified-compliance-api
  primary_region: ord
  
scaling:
  min_instances: 2
  max_instances: 10
  cpu_threshold: 70%
  memory_threshold: 80%
  
health_checks:
  path: /health
  interval: 30s
  timeout: 10s
  retries: 3
```

### 2. Vertical Scaling Patterns

#### Resource Optimization
```python
# Connection pooling configuration
DATABASE_POOL_SIZE = 20
DATABASE_POOL_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600

# Redis connection pooling
REDIS_POOL_SIZE = 10
REDIS_POOL_OVERFLOW = 20
REDIS_POOL_TIMEOUT = 30

# Async processing
MAX_WORKERS = 4
WORKER_TIMEOUT = 300
```

#### Performance Tuning
```python
# FastAPI configuration for high performance
app = FastAPI(
    title="Verified Compliance API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Performance optimizations
    openapi_url="/openapi.json",
    include_in_schema=True,
    # Middleware optimization
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"]),
        Middleware(GZipMiddleware, minimum_size=1000),
    ]
)

# Database optimization
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    future=True
)
```

### 3. Database Scaling Patterns

#### Read Replica Strategy
```sql
-- Master database for writes
CREATE DATABASE vc_master;

-- Read replicas for queries
CREATE DATABASE vc_replica_1;
CREATE DATABASE vc_replica_2;

-- Connection routing
-- Writes: vc_master
-- Reads: vc_replica_1, vc_replica_2 (round-robin)
```

#### Sharding Strategy
```python
# Database sharding by contact_id
class DatabaseRouter:
    def __init__(self, shard_count: int = 4):
        self.shard_count = shard_count
        self.shards = [
            f"postgresql://user:pass@shard-{i}.host:5432/vc_shard_{i}"
            for i in range(shard_count)
        ]
    
    def get_shard(self, contact_id: str) -> str:
        """Route to shard based on contact_id hash"""
        shard_index = hash(contact_id) % self.shard_count
        return self.shards[shard_index]
    
    def get_all_shards(self) -> List[str]:
        """Get all shard connections for cross-shard queries"""
        return self.shards
```

---

## Design Patterns

### 1. Repository Pattern

#### Backend Repository Implementation
```python
# ABSOLUTE IMPORT RULES - NO EXCEPTIONS
import abc
import typing
import sqlalchemy
import uuid
import datetime
import logging

# Base repository interface - REAL IMPLEMENTATION ONLY
class BaseRepository(abc.ABC):
    def __init__(self, db):
        self.db = db
    
    @abc.abstractmethod
    async def create(self, entity):
        """Create a new entity - REAL IMPLEMENTATION ONLY"""
        pass
    
    @abc.abstractmethod
    async def get_by_id(self, id):
        """Get entity by ID - REAL IMPLEMENTATION ONLY"""
        pass
    
    @abc.abstractmethod
    async def update(self, entity):
        """Update existing entity - REAL IMPLEMENTATION ONLY"""
        pass
    
    @abc.abstractmethod
    async def delete(self, id):
        """Delete entity by ID - REAL IMPLEMENTATION ONLY"""
        pass

# Concrete repository implementation - REAL IMPLEMENTATION ONLY
class ContactRepository(BaseRepository):
    async def create(self, contact):
        # REAL DATABASE OPERATION - NO MOCKS
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def get_by_id(self, id):
        # REAL DATABASE QUERY - NO MOCKS
        result = await self.db.execute(
            sqlalchemy.select(Contact).where(Contact.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email):
        # REAL DATABASE QUERY - NO MOCKS
        result = await self.db.execute(
            sqlalchemy.select(Contact).where(Contact.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update(self, contact):
        # REAL DATABASE OPERATION - NO MOCKS
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def delete(self, id):
        # REAL DATABASE OPERATION - NO MOCKS
        result = await self.db.execute(
            sqlalchemy.delete(Contact).where(Contact.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
```

### 2. Service Layer Pattern

#### Business Logic Services
```python
# Service layer with dependency injection
class ContactService:
    def __init__(
        self,
        contact_repo: ContactRepository,
        ghl_client: GHLClient,
        cache_service: CacheService
    ):
        self.contact_repo = contact_repo
        self.ghl_client = ghl_client
        self.cache_service = cache_service
    
    async def create_contact(self, contact_data: ContactCreate) -> Contact:
        """Create contact with GHL integration and caching"""
        # Check cache first
        cache_key = f"contact:email:{contact_data.email}"
        cached_contact = await self.cache_service.get(cache_key)
        if cached_contact:
            return Contact.from_dict(cached_contact)
        
        # Create local contact
        contact = Contact(**contact_data.dict())
        contact = await self.contact_repo.create(contact)
        
        # Sync with GHL
        try:
            ghl_contact_id = await self.ghl_client.upsert_contact(contact_data.dict())
            contact.ghl_contact_id = ghl_contact_id
            contact = await self.contact_repo.update(contact)
        except Exception as e:
            logger.error(f"GHL sync failed for contact {contact.id}: {e}")
        
        # Cache the result
        await self.cache_service.set(cache_key, contact.to_dict(), ttl=300)
        
        return contact
    
    async def get_contact_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by email with caching"""
        cache_key = f"contact:email:{email}"
        cached_contact = await self.cache_service.get(cache_key)
        if cached_contact:
            return Contact.from_dict(cached_contact)
        
        contact = await self.contact_repo.get_by_email(email)
        if contact:
            await self.cache_service.set(cache_key, contact.to_dict(), ttl=300)
        
        return contact
```

### 3. Factory Pattern

#### Service Factory
```python
# Service factory for dependency injection
class ServiceFactory:
    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache
        self._ghl_client = None
        self._email_client = None
    
    @property
    def ghl_client(self) -> GHLClient:
        if self._ghl_client is None:
            self._ghl_client = GHLClient(
                api_key=settings.GHL_API_KEY,
                location_id=settings.GHL_LOCATION_ID
            )
        return self._ghl_client
    
    @property
    def email_client(self) -> EmailClient:
        if self._email_client is None:
            self._email_client = EmailClient(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_pass=settings.SMTP_PASS
            )
        return self._email_client
    
    def create_contact_service(self) -> ContactService:
        contact_repo = ContactRepository(self.db)
        return ContactService(contact_repo, self.ghl_client, self.cache)
    
    def create_session_service(self) -> SessionService:
        session_repo = SessionRepository(self.db)
        return SessionService(session_repo, self.cache)
```

### 4. Observer Pattern

#### Event System
```python
# Event system with observers
from typing import List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    SESSION_STARTED = "session_started"
    SESSION_CHECKED_IN = "session_checked_in"
    SESSION_CHECKED_OUT = "session_checked_out"
    CONTACT_CREATED = "contact_created"

@dataclass
class Event:
    type: EventType
    data: dict
    timestamp: datetime
    source: str

class EventBus:
    def __init__(self):
        self._observers: List[Callable[[Event], None]] = []
    
    def subscribe(self, observer: Callable[[Event], None]):
        """Subscribe to events"""
        self._observers.append(observer)
    
    def unsubscribe(self, observer: Callable[[Event], None]):
        """Unsubscribe from events"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def publish(self, event: Event):
        """Publish event to all observers"""
        for observer in self._observers:
            try:
                await observer(event)
            except Exception as e:
                logger.error(f"Event observer failed: {e}")

# Event handlers
class GHLWebhookHandler:
    def __init__(self, ghl_client: GHLClient):
        self.ghl_client = ghl_client
    
    async def handle_session_completed(self, event: Event):
        """Send webhook to GHL when session is completed"""
        if event.type == EventType.SESSION_CHECKED_OUT:
            await self.ghl_client.send_webhook(event.data)

class NotificationHandler:
    def __init__(self, email_client: EmailClient):
        self.email_client = email_client
    
    async def handle_contact_created(self, event: Event):
        """Send welcome email to new contact"""
        if event.type == EventType.CONTACT_CREATED:
            await self.email_client.send_welcome_email(event.data["email"])
```

---

## Microservices Architecture

### 1. Service Decomposition Strategy

#### Current Monolith Structure
```
┌─────────────────────────────────────────────────────────────┐
│                    Monolithic Application                   │
├─────────────────────────────────────────────────────────────┤
│  API Gateway │  Auth Service │  Session Service │  GHL Service │
│  - Routes    │  - JWT        │  - Check-in/out │  - CRM Sync  │
│  - Validation│  - Users      │  - GPS Verify   │  - Webhooks  │
│  - Rate Limit│  - Permissions│  - Duration     │  - Tags      │
└─────────────────────────────────────────────────────────────┘
```

#### Future Microservices Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Microservices Architecture               │
├─────────────────────────────────────────────────────────────┤
│  API Gateway │  Auth Service │  Session Service │  GHL Service │
│  - Kong      │  - FastAPI    │  - FastAPI       │  - FastAPI   │
│  - Routing   │  - JWT        │  - PostgreSQL    │  - Redis     │
│  - Rate Limit│  - Redis      │  - Redis         │  - GHL API   │
│  - Auth      │  - PostgreSQL│  - Events        │  - Webhooks  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Service Communication Patterns

#### Synchronous Communication
```python
# HTTP client for service-to-service communication
class ServiceClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, endpoint: str, headers: dict = None) -> dict:
        """GET request to service"""
        response = await self.client.get(
            f"{self.base_url}{endpoint}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def post(self, endpoint: str, data: dict, headers: dict = None) -> dict:
        """POST request to service"""
        response = await self.client.post(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Service discovery
class ServiceRegistry:
    def __init__(self):
        self.services = {
            "auth": "http://auth-service:8000",
            "session": "http://session-service:8000",
            "ghl": "http://ghl-service:8000"
        }
    
    def get_service_url(self, service_name: str) -> str:
        """Get service URL by name"""
        return self.services.get(service_name)
```

#### Asynchronous Communication
```python
# Message queue for async communication
import asyncio
from typing import Dict, Any
import json

class MessageQueue:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.channels = {
            "session_events": "session:events",
            "ghl_webhooks": "ghl:webhooks",
            "notifications": "notifications"
        }
    
    async def publish(self, channel: str, message: Dict[Any, Any]):
        """Publish message to channel"""
        await self.redis.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to channel"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await handler(data)
```

### 3. Data Consistency Patterns

#### Saga Pattern
```python
# Saga pattern for distributed transactions
class SessionSaga:
    def __init__(self, session_service, ghl_service, notification_service):
        self.session_service = session_service
        self.ghl_service = ghl_service
        self.notification_service = notification_service
    
    async def execute_session_completion(self, session_data: dict):
        """Execute session completion saga"""
        saga_id = str(uuid4())
        steps = [
            self._complete_session,
            self._sync_to_ghl,
            self._send_notification
        ]
        
        try:
            for step in steps:
                await step(saga_id, session_data)
        except Exception as e:
            await self._compensate(saga_id, session_data, e)
    
    async def _complete_session(self, saga_id: str, session_data: dict):
        """Complete session step"""
        await self.session_service.complete_session(session_data)
    
    async def _sync_to_ghl(self, saga_id: str, session_data: dict):
        """Sync to GHL step"""
        await self.ghl_service.send_webhook(session_data)
    
    async def _send_notification(self, saga_id: str, session_data: dict):
        """Send notification step"""
        await self.notification_service.send_completion_email(session_data)
    
    async def _compensate(self, saga_id: str, session_data: dict, error: Exception):
        """Compensate for failed saga"""
        logger.error(f"Saga {saga_id} failed: {error}")
        # Implement compensation logic
```

---

## Event-Driven Architecture

### 1. Event Sourcing Pattern

#### Event Store
```python
# Event store for event sourcing
class EventStore:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def append_event(self, stream_id: str, event: Event):
        """Append event to stream"""
        event_record = EventRecord(
            stream_id=stream_id,
            event_type=event.type.value,
            event_data=event.data,
            timestamp=event.timestamp,
            version=await self._get_next_version(stream_id)
        )
        self.db.add(event_record)
        await self.db.commit()
    
    async def get_events(self, stream_id: str, from_version: int = 0) -> List[Event]:
        """Get events from stream"""
        result = await self.db.execute(
            select(EventRecord)
            .where(EventRecord.stream_id == stream_id)
            .where(EventRecord.version >= from_version)
            .order_by(EventRecord.version)
        )
        return [self._to_event(record) for record in result.scalars()]
    
    async def _get_next_version(self, stream_id: str) -> int:
        """Get next version for stream"""
        result = await self.db.execute(
            select(func.max(EventRecord.version))
            .where(EventRecord.stream_id == stream_id)
        )
        max_version = result.scalar()
        return (max_version or 0) + 1
```

#### Aggregate Pattern
```python
# Aggregate for session management
class SessionAggregate:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: List[Event] = []
        self._state = SessionState()
    
    def start_session(self, contact_id: str, meeting_id: str, destination: dict):
        """Start session command"""
        if self._state.is_started:
            raise InvalidOperationError("Session already started")
        
        event = Event(
            type=EventType.SESSION_STARTED,
            data={
                "session_id": self.session_id,
                "contact_id": contact_id,
                "meeting_id": meeting_id,
                "destination": destination
            },
            timestamp=datetime.utcnow(),
            source="session_aggregate"
        )
        self._apply_event(event)
    
    def check_in(self, coordinates: dict, accuracy: float):
        """Check in command"""
        if not self._state.is_started:
            raise InvalidOperationError("Session not started")
        
        if self._state.is_checked_in:
            raise InvalidOperationError("Already checked in")
        
        event = Event(
            type=EventType.SESSION_CHECKED_IN,
            data={
                "session_id": self.session_id,
                "coordinates": coordinates,
                "accuracy": accuracy
            },
            timestamp=datetime.utcnow(),
            source="session_aggregate"
        )
        self._apply_event(event)
    
    def _apply_event(self, event: Event):
        """Apply event to aggregate"""
        self.events.append(event)
        self._state.apply_event(event)
```

### 2. CQRS Pattern

#### Command Side
```python
# Command handlers
class SessionCommandHandler:
    def __init__(self, event_store: EventStore, session_repo: SessionRepository):
        self.event_store = event_store
        self.session_repo = session_repo
    
    async def handle_start_session(self, command: StartSessionCommand):
        """Handle start session command"""
        aggregate = SessionAggregate(command.session_id)
        aggregate.start_session(
            command.contact_id,
            command.meeting_id,
            command.destination
        )
        
        # Save events
        for event in aggregate.events:
            await self.event_store.append_event(command.session_id, event)
        
        # Update read model
        await self._update_read_model(aggregate)
    
    async def handle_check_in(self, command: CheckInCommand):
        """Handle check in command"""
        # Load aggregate from events
        events = await self.event_store.get_events(command.session_id)
        aggregate = SessionAggregate(command.session_id)
        for event in events:
            aggregate._apply_event(event)
        
        # Apply command
        aggregate.check_in(command.coordinates, command.accuracy)
        
        # Save new events
        for event in aggregate.events[len(events):]:
            await self.event_store.append_event(command.session_id, event)
        
        # Update read model
        await self._update_read_model(aggregate)
```

#### Query Side
```python
# Query handlers
class SessionQueryHandler:
    def __init__(self, read_db: AsyncSession):
        self.read_db = read_db
    
    async def get_session_by_id(self, session_id: str) -> Optional[SessionReadModel]:
        """Get session by ID"""
        result = await self.read_db.execute(
            select(SessionReadModel).where(SessionReadModel.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_sessions_by_contact(self, contact_id: str, limit: int = 20) -> List[SessionReadModel]:
        """Get sessions by contact"""
        result = await self.read_db.execute(
            select(SessionReadModel)
            .where(SessionReadModel.contact_id == contact_id)
            .order_by(SessionReadModel.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

---

## Caching Architecture

### 1. Multi-Layer Caching Strategy

#### Cache Hierarchy
```
┌─────────────────────────────────────────────────────────────┐
│                    Caching Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Browser      │  CDN         │  Application │  Database    │
│  - Local      │  - Static    │  - Redis     │  - Query     │
│  - Session    │  - API       │  - Memory    │  - Result    │
│  - Storage    │  - Global    │  - TTL       │  - Cache     │
└─────────────────────────────────────────────────────────────┘
```

#### Cache Implementation
```python
# Multi-layer cache service
class CacheService:
    def __init__(self, redis_url: str, memory_cache_size: int = 1000):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.memory_cache = {}
        self.memory_cache_size = memory_cache_size
    
    async def get(self, key: str) -> Optional[dict]:
        """Get from cache with fallback"""
        # Check memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check Redis cache
        cached = self.redis.get(key)
        if cached:
            data = json.loads(cached)
            # Store in memory cache
            self._store_in_memory(key, data)
            return data
        
        return None
    
    async def set(self, key: str, value: dict, ttl: int = 300):
        """Set cache with TTL"""
        # Store in memory cache
        self._store_in_memory(key, value)
        
        # Store in Redis cache
        self.redis.setex(key, ttl, json.dumps(value))
    
    def _store_in_memory(self, key: str, value: dict):
        """Store in memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.memory_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = value
```

### 2. Cache Invalidation Patterns

#### Cache-Aside Pattern
```python
# Cache-aside pattern implementation
class CachedSessionService:
    def __init__(self, session_repo: SessionRepository, cache: CacheService):
        self.session_repo = session_repo
        self.cache = cache
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session with cache-aside pattern"""
        cache_key = f"session:{session_id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return Session.from_dict(cached)
        
        # Load from database
        session = await self.session_repo.get_by_id(session_id)
        if session:
            # Store in cache
            await self.cache.set(cache_key, session.to_dict(), ttl=300)
        
        return session
    
    async def update_session(self, session: Session) -> Session:
        """Update session and invalidate cache"""
        # Update in database
        updated_session = await self.session_repo.update(session)
        
        # Invalidate cache
        cache_key = f"session:{session.id}"
        await self.cache.delete(cache_key)
        
        return updated_session
```

#### Write-Through Pattern
```python
# Write-through pattern implementation
class WriteThroughCache:
    def __init__(self, cache: CacheService, db: AsyncSession):
        self.cache = cache
        self.db = db
    
    async def create_session(self, session_data: dict) -> Session:
        """Create session with write-through cache"""
        # Create in database
        session = Session(**session_data)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        # Write to cache
        cache_key = f"session:{session.id}"
        await self.cache.set(cache_key, session.to_dict(), ttl=300)
        
        return session
    
    async def update_session(self, session: Session) -> Session:
        """Update session with write-through cache"""
        # Update in database
        await self.db.commit()
        await self.db.refresh(session)
        
        # Update cache
        cache_key = f"session:{session.id}"
        await self.cache.set(cache_key, session.to_dict(), ttl=300)
        
        return session
```

---

## Database Architecture

### 1. Database Design Patterns

#### Repository Pattern
```python
# Generic repository with type safety
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model_class: type[T]):
        self.db = db
        self.model_class = model_class
    
    async def create(self, **kwargs) -> T:
        """Create new entity"""
        entity = self.model_class(**kwargs)
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID"""
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all entities with pagination"""
        result = await self.db.execute(
            select(self.model_class)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def update(self, id: Any, **kwargs) -> Optional[T]:
        """Update entity by ID"""
        result = await self.db.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**kwargs)
            .returning(self.model_class)
        )
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID"""
        result = await self.db.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
```

#### Unit of Work Pattern
```python
# Unit of work for transaction management
class UnitOfWork:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._repositories = {}
    
    def get_repository(self, model_class: type[T]) -> BaseRepository[T]:
        """Get repository for model class"""
        if model_class not in self._repositories:
            self._repositories[model_class] = BaseRepository(self.db, model_class)
        return self._repositories[model_class]
    
    async def commit(self):
        """Commit all changes"""
        await self.db.commit()
    
    async def rollback(self):
        """Rollback all changes"""
        await self.db.rollback()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
```

### 2. Database Optimization Patterns

#### Connection Pooling
```python
# Database connection pool configuration
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

def create_database_engine(database_url: str) -> Engine:
    """Create database engine with connection pooling"""
    return create_async_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        future=True
    )

# Connection pool monitoring
class ConnectionPoolMonitor:
    def __init__(self, engine: Engine):
        self.engine = engine
    
    async def get_pool_status(self) -> dict:
        """Get connection pool status"""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
```

#### Query Optimization
```python
# Query optimization patterns
class OptimizedSessionRepository(BaseRepository[Session]):
    async def get_sessions_by_contact_optimized(
        self, 
        contact_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Session]:
        """Optimized query for sessions by contact"""
        query = (
            select(Session)
            .where(Session.contact_id == contact_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_nearby_meetings(
        self, 
        lat: float, 
        lng: float, 
        radius: int = 1000
    ) -> List[Meeting]:
        """Spatial query for nearby meetings"""
        query = select(Meeting).where(
            func.ST_DWithin(
                Meeting.location,
                func.ST_MakePoint(lng, lat),
                radius
            )
        ).limit(25)
        
        result = await self.db.execute(query)
        return result.scalars().all()
```

---

## API Architecture

### 1. RESTful API Design

#### Resource-Based URLs
```python
# RESTful API endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(prefix="/api/v1", tags=["sessions"])

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Create a new session"""
    try:
        session = await session_service.create_session(session_data, current_user.id)
        return SessionResponse(success=True, data=session)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get session by ID"""
    session = await session_service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(success=True, data=session)

@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Update session"""
    try:
        session = await session_service.update_session(session_id, session_data, current_user.id)
        return SessionResponse(success=True, data=session)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Delete session"""
    success = await session_service.delete_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
```

#### API Versioning Strategy
```python
# API versioning with backward compatibility
from fastapi import FastAPI, APIRouter

# Version 1 API
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

@v1_router.get("/sessions")
async def get_sessions_v1():
    """Version 1 sessions endpoint"""
    pass

# Version 2 API
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v2_router.get("/sessions")
async def get_sessions_v2():
    """Version 2 sessions endpoint with enhanced features"""
    pass

# Main app with versioned routers
app = FastAPI(title="Verified Compliance API")
app.include_router(v1_router)
app.include_router(v2_router)

# Deprecation headers
@app.middleware("http")
async def add_deprecation_headers(request: Request, call_next):
    response = await call_next(request)
    
    if request.url.path.startswith("/api/v1"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31"
        response.headers["Link"] = "</api/v2>; rel=\"successor-version\""
    
    return response
```

### 2. API Gateway Pattern

#### Gateway Configuration
```python
# API Gateway with routing and middleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx

app = FastAPI(title="Verified Compliance API Gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.verifiedcompliance.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.verifiedcompliance.com", "*.verifiedcompliance.com"]
)

# Service routing
SERVICE_ROUTES = {
    "auth": "http://auth-service:8000",
    "sessions": "http://session-service:8000",
    "contacts": "http://contact-service:8000",
    "ghl": "http://ghl-service:8000"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service: str, path: str, request: Request):
    """Proxy request to appropriate service"""
    if service not in SERVICE_ROUTES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_url = SERVICE_ROUTES[service]
    target_url = f"{service_url}/{path}"
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=request.headers,
            params=request.query_params,
            content=await request.body()
        )
    
    return response.json()
```

---

## Mobile Architecture

### 1. Flutter Architecture Patterns

#### Clean Architecture
```dart
// Clean architecture layers
lib/
├── domain/                    # Business logic
│   ├── entities/             # Domain entities
│   ├── repositories/         # Repository interfaces
│   └── usecases/            # Use cases
├── data/                     # Data layer
│   ├── models/              # Data models
│   ├── repositories/         # Repository implementations
│   ├── services/            # API services
│   └── local/              # Local storage
├── presentation/             # UI layer
│   ├── pages/              # Screens
│   ├── widgets/            # Reusable widgets
│   ├── providers/          # State management
│   └── controllers/        # Business logic controllers
└── core/                    # Core utilities
    ├── constants.dart
    ├── errors.dart
    └── network.dart
```

#### Repository Pattern Implementation
```dart
// Repository interface
abstract class SessionRepository {
  Future<Session> startSession(SessionStartRequest request);
  Future<CheckInResponse> checkIn(String sessionId, CheckInRequest request);
  Future<CheckOutResponse> checkOut(String sessionId, CheckOutRequest request);
  Future<List<Session>> getSessions(String contactId, {int page = 1, int limit = 20});
  Future<void> syncPendingSessions();
}

// Repository implementation
class SessionRepositoryImpl implements SessionRepository {
  final ApiService _apiService;
  final LocalStorageService _localStorage;
  final ConnectivityService _connectivity;
  
  SessionRepositoryImpl(this._apiService, this._localStorage, this._connectivity);
  
  @override
  Future<Session> startSession(SessionStartRequest request) async {
    try {
      if (await _connectivity.isConnected()) {
        final response = await _apiService.startSession(request);
        await _localStorage.saveSession(response.session);
        return response.session;
      } else {
        // Save for later sync
        final session = Session.fromRequest(request);
        await _localStorage.saveSession(session);
        return session;
      }
    } catch (e) {
      throw SessionException('Failed to start session: $e');
    }
  }
  
  @override
  Future<CheckInResponse> checkIn(String sessionId, CheckInRequest request) async {
    try {
      if (await _connectivity.isConnected()) {
        return await _apiService.checkIn(sessionId, request);
      } else {
        // Save for later sync
        await _localStorage.saveCheckIn(sessionId, request);
        return CheckInResponse(ok: true, checkInTs: DateTime.now());
      }
    } catch (e) {
      throw SessionException('Failed to check in: $e');
    }
  }
}
```

### 2. State Management Patterns

#### Provider Pattern
```dart
// Provider-based state management
class SessionNotifier extends ChangeNotifier {
  final SessionRepository _repository;
  final LocationService _locationService;
  
  Session? _currentSession;
  bool _isLoading = false;
  String? _error;
  List<Session> _sessions = [];
  
  // Getters
  Session? get currentSession => _currentSession;
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Session> get sessions => _sessions;
  
  // Actions
  Future<void> startSession(SessionStartRequest request) async {
    _setLoading(true);
    _clearError();
    
    try {
      final session = await _repository.startSession(request);
      _currentSession = session;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> checkIn(CheckInRequest request) async {
    if (_currentSession == null) return;
    
    _setLoading(true);
    _clearError();
    
    try {
      final position = await _locationService.getCurrentLocation();
      request.coords = Coordinates(
        lat: position.latitude,
        lng: position.longitude,
        accuracy: position.accuracy,
      );
      
      await _repository.checkIn(_currentSession!.id, request);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }
  
  void _clearError() {
    _error = null;
    notifyListeners();
  }
}
```

#### BLoC Pattern
```dart
// BLoC pattern for complex state management
class SessionBloc extends Bloc<SessionEvent, SessionState> {
  final SessionRepository _repository;
  final LocationService _locationService;
  
  SessionBloc(this._repository, this._locationService) : super(SessionInitial()) {
    on<StartSessionEvent>(_onStartSession);
    on<CheckInEvent>(_onCheckIn);
    on<CheckOutEvent>(_onCheckOut);
  }
  
  Future<void> _onStartSession(StartSessionEvent event, Emitter<SessionState> emit) async {
    emit(SessionLoading());
    
    try {
      final session = await _repository.startSession(event.request);
      emit(SessionStarted(session));
    } catch (e) {
      emit(SessionError(e.toString()));
    }
  }
  
  Future<void> _onCheckIn(CheckInEvent event, Emitter<SessionState> emit) async {
    emit(SessionLoading());
    
    try {
      final position = await _locationService.getCurrentLocation();
      final request = CheckInRequest(
        coords: Coordinates(
          lat: position.latitude,
          lng: position.longitude,
          accuracy: position.accuracy,
        ),
        clientTs: DateTime.now(),
      );
      
      final response = await _repository.checkIn(event.sessionId, request);
      emit(SessionCheckedIn(response));
    } catch (e) {
      emit(SessionError(e.toString()));
    }
  }
}
```

---

## DevOps Architecture

### 1. CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# Complete CI/CD pipeline
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  FLUTTER_VERSION: '3.16.0'

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
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: |
          poetry run pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t verified-compliance-api .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag verified-compliance-api ${{ secrets.DOCKER_USERNAME }}/verified-compliance-api:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/verified-compliance-api:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          flyctl deploy --remote-only
```

### 2. Infrastructure as Code

#### Docker Configuration
```dockerfile
# Multi-stage Docker build
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Docker Compose
```yaml
# Development environment
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/vc_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=vc_dev
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 3. Monitoring and Observability

#### Application Monitoring
```python
# Comprehensive monitoring setup
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Sentry configuration
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(auto_enabling=True),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_SESSIONS = Gauge('active_sessions_total', 'Number of active sessions')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')

# Start metrics server
start_http_server(8000)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

---

This comprehensive architecture document provides detailed system design patterns, scalability considerations, and implementation guidelines for the Verified Compliance system. The architecture is designed to be scalable, maintainable, and secure while meeting the specific requirements of a mobile attendance tracking application.
