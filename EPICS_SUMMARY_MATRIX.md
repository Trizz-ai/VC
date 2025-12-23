# Verified Compliance™ — Epic Summary & Priority Matrix

## Quick Reference Guide

This document provides a high-level overview of all epics (original + new) and their relationships.

---

## EPIC MAPPING: Original ↔ New

| Original Epic | New Epic(s) | Relationship |
|--------------|-------------|--------------|
| EPIC 1: User Onboarding | V2-2 (2FA), V2-3 (Mandates) | **Extended** - Original basic onboarding now requires 2FA and consent artifacts |
| EPIC 2: Meeting Discovery | (Unchanged) | **Retained** - No changes needed |
| EPIC 3: Check-In/Check-Out | V2-4 (Documentation Workflow), V2-5 (Offline) | **Significantly Extended** - Now includes biometrics, immutability, receipts |
| EPIC 4: Activity Logs | V2-8 (Professional Review) | **Extended** - Professionals get review queue, individuals retain log viewing |
| EPIC 5: Public Share | V2-10 (Reports & QR) | **Extended** - Server-side generation, verification proofs |
| EPIC 6: GHL Integration | (Unchanged) | **Retained** - May need minor updates for new data fields |
| EPIC 7: Security | V2-11 (Audit), V2-19 (Access), V2-20 (Temporal) | **Significantly Extended** - Comprehensive audit chain, access governance |
| EPIC 8: Offline Support | V2-5 (Offline Capture) | **Merged & Extended** - Encrypted queue, dual timestamps |
| EPIC 9: Admin & Meetings | V2-14 (Policy Engine), V2-21 (Credentials) | **Extended** - Jurisdiction policies, professional credentials |
| EPIC 10: Analytics | (Unchanged) | **Retained** - No changes needed |
| EPIC 11: QR Campaigns | (Unchanged) | **Retained** - No changes needed |
| EPIC 12-15: Testing/DevOps | (Unchanged) | **Retained** - Apply to all new features |

---

## NEW EPICS (V2) SUMMARY

| Epic | Name | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| V2-1 | Terminology Standards | P0 | Small | None |
| V2-2 | 2FA & Identity | P0 | Large | V2-1 |
| V2-3 | Mandate Enrollment | P0 | Large | V2-2 |
| V2-4 | Documentation Workflow | P0 | XLarge | V2-2, V2-3 |
| V2-5 | Offline Capture | P1 | Medium | V2-4 |
| V2-6 | Emergency Explanations | P1 | Medium | V2-4 |
| V2-7 | Data Quality Signals | P1 | Medium | V2-4 |
| V2-8 | Professional Review | P0 | Large | V2-4, V2-7 |
| V2-9 | In-App Messaging | P1 | Large | V2-3, V2-8 |
| V2-10 | Reports & QR | P0 | Medium | V2-4 |
| V2-11 | Audit Chain | P0 | Large | V2-1 |
| V2-12 | Ad Isolation | P2 | Small | None |
| V2-13 | AI Concierge | P2 | Medium | V2-11 |
| V2-14 | Policy Engine | P1 | Medium | V2-2 |
| V2-15 | Accessibility | P1 | Medium | None |
| V2-16 | System Resilience | P1 | Medium | V2-5 |
| V2-17 | Retention & Legal Hold | P0 | Medium | V2-11 |
| V2-18 | Subpoena Handling | P1 | Small | V2-11, V2-17 |
| V2-19 | Staff Access | P1 | Small | V2-11 |
| V2-20 | Temporal Integrity | P1 | Small | V2-4 |
| V2-21 | Credential Lifecycle | P0 | Medium | V2-8 |
| V2-22 | Stripe Billing | P2 | Medium | None |
| V2-23 | Verification Provider | P1 | Large | V2-10, V2-11 |

---

## PRIORITY DEFINITIONS

| Priority | Definition | Timeline |
|----------|------------|----------|
| **P0** | Critical for legal/compliance positioning | Must ship Phase 1 |
| **P1** | Required for commercial viability | Must ship Phase 2 |
| **P2** | Important for monetization/UX | Can ship Phase 3 |

---

## PHASED DELIVERY PLAN

### Phase 1: Foundation & Legal Compliance (Weeks 1-8)
**Goal:** Establish documentation-not-verification positioning

| Week | Epics | Deliverables |
|------|-------|--------------|
| 1-2 | V2-1, V2-11 | Terminology enforcement, Audit foundation |
| 3-4 | V2-2 | 2FA system, Consent artifacts |
| 5-6 | V2-3 | Mandate creation, SMS enrollment |
| 7-8 | V2-4 (partial) | Enhanced check-in with biometrics |

**Milestone:** Professional can create mandate, individual can enroll and check-in with full audit trail.

### Phase 2: Professional Workflow (Weeks 9-16)
**Goal:** Complete professional review capabilities

| Week | Epics | Deliverables |
|------|-------|--------------|
| 9-10 | V2-4 (complete), V2-7 | Full documentation workflow, Quality signals |
| 11-12 | V2-8, V2-21 | Professional review queue, Credential management |
| 13-14 | V2-5, V2-6 | Offline support, Emergency explanations |
| 15-16 | V2-10, V2-17 | Reports with QR, Retention policies |

**Milestone:** End-to-end workflow from mandate creation to professional review decision.

### Phase 3: Advanced Features (Weeks 17-24)
**Goal:** Feature completeness and monetization

| Week | Epics | Deliverables |
|------|-------|--------------|
| 17-18 | V2-9 | In-app messaging |
| 19-20 | V2-23 | Verification provider framework |
| 21-22 | V2-14, V2-15 | Policy engine, Accessibility |
| 23-24 | V2-22, V2-12 | Stripe billing, Ad isolation |

**Milestone:** Commercially viable product with subscription billing.

---

## DATABASE SCHEMA ADDITIONS

### New Tables (by Phase)

**Phase 1:**
```
consent_artifacts
verification_codes
user_identities
jurisdictions
policy_versions
review_artifacts
audit_entries
mandates
enrollment_tokens
sms_delivery_logs
```

**Phase 2:**
```
selfie_artifacts
data_quality_signals
emergency_explanations
explanation_attachments
professional_credentials
report_templates
vc_reports
legal_holds
record_tombstones
```

**Phase 3:**
```
message_threads
messages
message_attachments
sla_tracking
verification_proofs
subscriptions
incidents
```

### Modified Tables

**contacts:**
- +phone_verified, phone_verified_at
- +email_verified, email_verified_at
- +twofa_enabled, twofa_setup_completed_at
- +totp_secret_encrypted

**session_events:**
- +selfie_artifact_id
- +liveness_score, liveness_passed
- +device_timestamp, server_receipt_timestamp
- +context_notes
- +receipt_id
- +policy_version_id

---

## API ENDPOINTS ADDITIONS

### Phase 1 Endpoints
```
POST   /api/v1/verification/phone/send
POST   /api/v1/verification/phone/verify
POST   /api/v1/verification/email/send
POST   /api/v1/verification/email/verify
POST   /api/v1/verification/totp/setup
POST   /api/v1/verification/totp/verify
GET    /api/v1/verification/status

POST   /api/v1/consent
GET    /api/v1/consent
GET    /api/v1/consent/required
GET    /api/v1/consent/export

POST   /api/v1/mandates
GET    /api/v1/mandates
GET    /api/v1/mandates/{id}
POST   /api/v1/mandates/{id}/send-sms
POST   /api/v1/mandates/enroll

POST   /api/v1/reviews
GET    /api/v1/reviews/{record_id}
GET    /api/v1/reviews/export
```

### Phase 2 Endpoints
```
GET    /api/v1/professional/queue
GET    /api/v1/professional/records/{id}
POST   /api/v1/professional/records/{id}/decide
POST   /api/v1/professional/records/{id}/annotate

POST   /api/v1/explanations
POST   /api/v1/explanations/{id}/attachments
GET    /api/v1/explanations
GET    /api/v1/explanations/{id}

POST   /api/v1/reports/generate
GET    /api/v1/reports/{id}
GET    /api/v1/public/verify/{token}
```

### Phase 3 Endpoints
```
POST   /api/v1/messages/threads
GET    /api/v1/messages/threads/{id}
POST   /api/v1/messages/threads/{id}/messages
POST   /api/v1/messages/{id}/attachments
GET    /api/v1/messages/threads
POST   /api/v1/messages/export

POST   /api/v1/subscriptions/create-checkout-session
POST   /api/v1/subscriptions/webhook
GET    /api/v1/subscriptions/status
POST   /api/v1/subscriptions/cancel
```

---

## RISK REGISTER (Updated)

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Terminology slip in code | High | Medium | CI/CD enforcement |
| 2FA friction reduces adoption | Medium | Medium | Streamlined UX, clear value prop |
| SMS delivery failures | High | Low | Multiple providers, fallback options |
| Liveness detection false positives | Medium | Medium | Quality threshold tuning |
| Audit log gaps | Critical | Low | Transaction-based logging |
| Legal hold not preventing deletion | Critical | Low | Database constraints + service checks |
| Verification proof delays | Medium | Medium | Async processing, retry logic |
| Stripe webhook failures | High | Low | Idempotency, retry queue |

---

## SUCCESS METRICS

### Phase 1 Success Criteria
- [ ] Zero prohibited terms in production code
- [ ] 100% of users complete 2FA before first check-in
- [ ] 100% of sessions have consent artifacts
- [ ] Audit chain integrity verifiable

### Phase 2 Success Criteria
- [ ] Professional review queue < 24hr SLA
- [ ] 95%+ records have all quality signals
- [ ] Offline sync success rate > 99%
- [ ] Zero mutable records post-submission

### Phase 3 Success Criteria
- [ ] Message export generation < 30 seconds
- [ ] Verification proof coverage 100%
- [ ] Subscription conversion > 5%
- [ ] WCAG 2.1 AA audit pass

---

## TEAM ALLOCATION RECOMMENDATION

| Role | Phase 1 Focus | Phase 2 Focus | Phase 3 Focus |
|------|--------------|---------------|---------------|
| Backend Dev 1 | 2FA, Consent, Audit | Review Service, Credentials | Messaging, Verification |
| Backend Dev 2 | Mandates, Enrollment | Quality Signals, Reports | Policy Engine, Billing |
| Frontend Dev 1 | 2FA Flow, Consent UI | Check-In Capture | Professional Web |
| Frontend Dev 2 | Enrollment Flow | Offline Queue | Messaging UI |
| QA | Integration Tests | E2E Tests | Load Testing |

---

**END OF SUMMARY MATRIX**

