# Cursor Rules for Verified Compliance Development

> **CRITICAL**: These rules enforce the Ironclad Development Rules from best_practices.md. All VC development must follow these guidelines.

## 🔒 TIER 1: ABSOLUTE RULES (NEVER VIOLATE)

### Rule 1.1: GPS & Location Data
**NEVER track location in the background. Period.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Uses background location services
- Tracks location continuously
- Uses LocationPermission.always in Flutter
- Captures GPS outside of check_in/check_out functions

// ✅ CORRECT - Only allow:
- Location capture during explicit user actions
- LocationPermission.whileInUse in Flutter
- GPS capture only in check_in() and check_out() functions
- Log all GPS captures with user action context
```

### Rule 1.2: Data Encryption & Secrets
**NEVER commit secrets, API keys, or credentials to version control. EVER.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Hard-codes secrets, API keys, or credentials
- Commits .env files with real values
- Uses production secrets in development code
- Exposes sensitive data in logs or comments

// ✅ CORRECT - Only allow:
- Environment variables for all secrets
- .env.example files with placeholder values
- Proper secret management (GitHub Secrets, Fly.io Secrets)
- Scrub sensitive data from logs
```

### Rule 1.3: Database Migrations
**NEVER modify the database schema without a migration. NEVER run manual SQL in production.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Modifies database schema without Alembic migration
- Runs manual SQL in production
- Skips migration testing on staging
- Creates irreversible schema changes

// ✅ CORRECT - Only allow:
- All schema changes via Alembic migrations
- Migrations tested on staging before production
- Reversible migrations with downgrade() function
- Proper migration versioning and documentation
```

### Rule 1.4: Personal Data Protection
**NEVER log, display, or transmit PII without explicit need. Treat all user data as confidential.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Logs PII (email, phone, full names, GPS coordinates)
- Displays sensitive data in error messages
- Transmits PII without encryption
- Stores PII without proper consent

// ✅ CORRECT - Only allow:
- Partial IDs in logs (first 8 characters)
- Encrypted PII at rest
- Proper consent flows
- PII scrubbing in error tracking
```

### Rule 1.5: Authentication & Authorization
**NEVER trust client-side data. ALWAYS validate ownership server-side.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Trusts client-side data for authorization
- Skips ownership verification
- Allows unauthorized access to resources
- Uses weak authentication mechanisms

// ✅ CORRECT - Only allow:
- Server-side validation for all protected endpoints
- Ownership verification: resource.contact_id == current_contact.id
- JWT tokens with 15-minute expiration
- Rate limiting on all endpoints
```

### Rule 1.6: GPS Verification Integrity
**NEVER fake, bypass, or weaken GPS verification. The 200m threshold is sacred.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Bypasses GPS verification
- Weakens the 200m threshold
- Allows exceptions to location verification
- Fakes location data

// ✅ CORRECT - Only allow:
- Hard-coded 200m threshold (never configurable)
- Immutable location flags once set
- Independent haversine distance calculation
- Log all flagged sessions for review
```

### Rule 1.7: API Backwards Compatibility
**NEVER break existing API contracts. ALWAYS version breaking changes.**

```cursor
// ❌ FORBIDDEN - Reject any code that:
- Breaks existing API contracts
- Removes fields from responses
- Changes field types without versioning
- Adds required fields to existing endpoints

// ✅ CORRECT - Only allow:
- Versioned endpoints for breaking changes
- Backwards compatible changes
- Proper deprecation warnings
- Support old versions for minimum 6 months
```

## 🛡️ TIER 2: CRITICAL BEST PRACTICES (STRONG RECOMMENDATIONS)

### Rule 2.1: Error Handling & Graceful Degradation
```cursor
// ✅ REQUIRED - All code must:
- Handle external service failures gracefully
- Never block core functionality due to external failures
- Provide clear error messages to users
- Log errors with proper context
- Implement retry mechanisms for transient failures
```

### Rule 2.2: Database Queries & Performance
```cursor
// ✅ REQUIRED - All database code must:
- Use proper indexes for query columns
- Avoid N+1 queries
- Implement pagination for lists
- Target 95th percentile response time < 300ms
- Use EXPLAIN ANALYZE for slow queries
```

### Rule 2.3: Testing Requirements
```cursor
// ✅ REQUIRED - All code must:
- Have minimum 80% line coverage (backend)
- Have minimum 70% line coverage (Flutter)
- Include tests for critical paths (100% coverage)
- Test error conditions and edge cases
- Include integration tests for API endpoints
```

### Rule 2.4: Code Review Standards
```cursor
// ✅ REQUIRED - All PRs must:
- Have approval from 2 reviewers
- Pass security review checklist
- Pass data privacy review
- Pass code quality review
- Include comprehensive tests
```

### Rule 2.5: Deployment Process
```cursor
// ✅ REQUIRED - All deployments must:
- Deploy to staging first
- Pass QA testing on staging
- Include rollback plan
- Monitor error rates and performance
- Follow deployment checklist
```

### Rule 2.6: Logging & Monitoring
```cursor
// ✅ REQUIRED - All code must:
- Log important business events
- Never log sensitive data
- Use proper log levels
- Include structured logging with context
- Set up monitoring alerts
```

## 🎯 TIER 3: DEVELOPMENT WORKFLOW (CONSISTENCY & QUALITY)

### Rule 3.1: Git Workflow & Branch Strategy
```cursor
// ✅ REQUIRED - All development must:
- Use proper branch naming: feature/VC-123-description
- Follow commit message format: type(scope): description
- Include ticket numbers in PR titles
- Keep branches up-to-date with main
```

### Rule 3.2: Code Style & Formatting
```cursor
// ✅ REQUIRED - All code must:
- Use black for Python formatting
- Use isort for Python imports
- Use dart format for Flutter
- Follow naming conventions
- Pass linting checks
```

### Rule 3.3: Documentation Standards
```cursor
// ✅ REQUIRED - All code must:
- Include module docstrings
- Document all public functions
- Update API documentation
- Include README for features
- Document configuration options
```

### Rule 3.4: Environment Management
```cursor
// ✅ REQUIRED - All environments must:
- Use proper environment variables
- Never commit real secrets
- Follow secret rotation schedule
- Use staging for testing
- Monitor production health
```

## 🚨 INCIDENT RESPONSE PROCEDURES

### Critical Incident Classification
```cursor
// ✅ REQUIRED - All incidents must:
- Be classified by severity (P0-P3)
- Follow incident response process
- Include post-mortem for P0/P1
- Document timeline and root cause
- Implement prevention measures
```

## 📋 DEFINITION OF DONE

### Feature Completion Requirements
```cursor
// ✅ REQUIRED - Features are NOT done until:
- Code complete and follows style guide
- Unit tests written (80% coverage)
- Integration tests written
- Code reviewed and approved by 2 engineers
- Documentation updated
- Tested on staging environment
- QA testing completed
- Security review passed
- Performance tested
- Database migrations tested
- Backwards compatibility verified
- Error handling comprehensive
- Logging added for key events
- Monitoring/alerts configured
- Deployed to production
- Post-deployment smoke tests passed
- Stakeholders notified
- Ticket closed and demo recorded
```

## 🎓 ONBOARDING CHECKLIST

### New Developer Requirements
```cursor
// ✅ REQUIRED - New developers must:
- Complete development environment setup
- Read and acknowledge these rules
- Complete one small bug fix
- Shadow code review process
- Review system architecture
- Understand GPS verification logic
- Complete first feature with mentor
- Write tests for feature
- Submit PR for review
- Deploy to staging
- Complete feature independently
- Participate in code reviews
- Understand deployment process
- Be ready for on-call rotation
```

## 📞 SUPPORT & ESCALATION

### Issue Resolution Process
```cursor
// ✅ REQUIRED - All issues must:
- Check documentation first
- Ask in team Slack (#dev-help)
- Create GitHub issue if needed
- Escalate to tech lead if unresolved
- Follow security incident process for security issues
- Follow incident response process for production issues
```

## ✅ ACKNOWLEDGMENT

### Team Commitment
```cursor
// ✅ REQUIRED - All team members must:
- Read and understand these rules
- Follow all Tier 1 rules without exception
- Adhere to Tier 2 best practices
- Maintain code quality standards
- Prioritize security and privacy
- Report violations when observed
- Sign acknowledgment form
```

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Review Frequency:** Quarterly
