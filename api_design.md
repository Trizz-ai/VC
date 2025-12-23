# Verified Compliance - API Design Document

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Core Endpoints](#core-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Webhooks](#webhooks)
8. [API Versioning](#api-versioning)

---

## API Overview

### Base URL
```
Production: https://api.verifiedcompliance.com/api/v1
Staging: https://staging-api.verifiedcompliance.com/api/v1
Development: http://localhost:8080/api/v1
```

### Content Type
All requests and responses use `application/json` content type.

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## Authentication & Authorization

### JWT Token Authentication
All protected endpoints require a JWT Bearer token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

### Token Lifecycle
- **Access Token**: 15 minutes expiration
- **Refresh Token**: 7 days expiration
- **Session Token**: 15 minutes expiration (for active sessions)
- **Public Token**: 30 days expiration (for public shares)

### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "contact_id",
    "iat": 1640995200,
    "exp": 1640996100,
    "type": "access",
    "scope": "user"
  }
}
```

### Authorization Rules
- Users can only access their own sessions
- Admin endpoints require special admin tokens
- Public share pages require valid public tokens
- Rate limiting: 100 requests/minute per IP

---

## Core Endpoints

### Contact Management

#### Create Contact
```http
POST /contacts
Content-Type: application/json

{
  "email": "user@example.com",
  "phone": "+15555551234",
  "first_name": "John",
  "last_name": "Doe",
  "consent_granted": true
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "contact_id": "uuid",
    "ghl_contact_id": "ghl_abc123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "consent_granted": true,
    "created_at": "2025-01-01T12:00:00Z"
  },
  "message": "Contact created successfully"
}
```

#### Get Contact
```http
GET /contacts/{contact_id}
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "contact_id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "consent_granted": true,
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
}
```

#### Update Contact
```http
PATCH /contacts/{contact_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "contact_id": "uuid",
    "email": "user@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "consent_granted": true,
    "updated_at": "2025-01-01T12:30:00Z"
  },
  "message": "Contact updated successfully"
}
```

### Meeting Discovery

#### Find Nearby Meetings
```http
GET /meetings/nearby?lat=38.5816&lng=-121.4944&limit=25&radius=5000
Authorization: Bearer <token>
```

**Query Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `limit` (optional): Maximum number of results (default: 25)
- `radius` (optional): Search radius in meters (default: 5000)
- `category` (optional): Filter by category (AA, NA, Gym, etc.)

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "meetings": [
      {
        "id": "uuid",
        "name": "Downtown AA Meeting",
        "description": "Open meeting for all",
        "address": "123 Main St, Sacramento CA 95814",
        "lat": 38.5816,
        "lng": -121.4944,
        "distance_meters": 450,
        "category": "AA",
        "timezone": "America/Los_Angeles",
        "start_time": "2025-01-01T19:00:00Z",
        "end_time": "2025-01-01T20:00:00Z",
        "is_active": true
      }
    ],
    "total": 25,
    "radius_meters": 5000
  }
}
```

#### Search Meetings
```http
GET /meetings/search?q=downtown&lat=38.5816&lng=-121.4944&limit=25
Authorization: Bearer <token>
```

**Query Parameters:**
- `q` (required): Search query (minimum 3 characters)
- `lat` (optional): Latitude for distance sorting
- `lng` (optional): Longitude for distance sorting
- `limit` (optional): Maximum number of results (default: 25)

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "meetings": [
      {
        "id": "uuid",
        "name": "Downtown AA Meeting",
        "address": "123 Main St, Sacramento CA",
        "lat": 38.5816,
        "lng": -121.4944,
        "distance_meters": 450,
        "category": "AA",
        "relevance_score": 0.95
      }
    ],
    "total": 5,
    "query": "downtown"
  }
}
```

### Session Management

#### Start Session
```http
POST /sessions/start
Content-Type: application/json
Authorization: Bearer <token>

{
  "contact_id": "uuid",
  "meeting_id": "uuid",
  "dest_name": "Downtown AA Meeting",
  "dest_address": "123 Main St, Sacramento CA",
  "dest_lat": 38.5816,
  "dest_lng": -121.4944,
  "source": "app"
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "session_token": "short_token_abc123",
    "expires_at": "2025-01-01T12:15:00Z",
    "dest_name": "Downtown AA Meeting",
    "dest_address": "123 Main St, Sacramento CA",
    "dest_lat": 38.5816,
    "dest_lng": -121.4944
  },
  "message": "Session started successfully"
}
```

#### Check In
```http
POST /sessions/{session_id}/check-in
Content-Type: application/json
Authorization: Bearer <token>

{
  "session_token": "short_token_abc123",
  "coords": {
    "lat": 38.5817,
    "lng": -121.4945,
    "accuracy": 12
  },
  "client_ts": "2025-01-01T12:00:00Z"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "ok": true,
    "check_in_ts": "2025-01-01T12:00:02Z",
    "location_flag": "granted",
    "distance_meters": 45,
    "session_status": "active"
  },
  "message": "Check-in successful"
}
```

#### Add Session Notes
```http
PATCH /sessions/{session_id}/notes
Content-Type: application/json
Authorization: Bearer <token>

{
  "session_token": "short_token_abc123",
  "notes": "Great meeting today, learned a lot about recovery",
  "client_ts": "2025-01-01T12:15:00Z"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "ok": true,
    "notes": "Great meeting today, learned a lot about recovery",
    "updated_at": "2025-01-01T12:15:00Z"
  },
  "message": "Notes updated successfully"
}
```

#### Check Out
```http
POST /sessions/{session_id}/check-out
Content-Type: application/json
Authorization: Bearer <token>

{
  "session_token": "short_token_abc123",
  "coords": {
    "lat": 38.5818,
    "lng": -121.4946,
    "accuracy": 15
  },
  "client_ts": "2025-01-01T13:04:00Z"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "ok": true,
    "check_out_ts": "2025-01-01T13:04:03Z",
    "duration_minutes": 64,
    "location_flag": "granted",
    "public_token": "pub_xyz789",
    "session_status": "complete"
  },
  "message": "Check-out successful"
}
```

#### Get Session Status
```http
GET /sessions/{session_id}/status
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "active",
    "expires_at": "2025-01-01T12:15:00Z",
    "is_checked_in": true,
    "is_checked_out": false,
    "elapsed_minutes": 15
  }
}
```

### Activity Logs

#### Get User Sessions
```http
GET /sessions?contact_id=uuid&page=1&per_page=20&range=30d&category=AA&query=downtown
Authorization: Bearer <token>
```

**Query Parameters:**
- `contact_id` (required): User's contact ID
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `range` (optional): Date range (7d, 30d, 90d, custom)
- `from` (optional): Start date (YYYY-MM-DD)
- `to` (optional): End date (YYYY-MM-DD)
- `category` (optional): Filter by category
- `query` (optional): Search query
- `group_by` (optional): Group by destination

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "uuid",
        "dest_name": "Downtown AA Meeting",
        "dest_address": "123 Main St",
        "check_in_ts": "2025-01-01T12:00:00Z",
        "check_out_ts": "2025-01-01T13:04:00Z",
        "duration_minutes": 64,
        "location_flag": "granted",
        "notes": "Great meeting today",
        "category": "AA",
        "public_token": "pub_xyz",
        "created_at": "2025-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 47,
      "pages": 3
    },
    "filters": {
      "range": "30d",
      "category": "AA",
      "query": "downtown"
    }
  }
}
```

#### Get Session Details
```http
GET /sessions/{session_id}
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "contact_id": "uuid",
    "meeting_id": "uuid",
    "dest_name": "Downtown AA Meeting",
    "dest_address": "123 Main St, Sacramento CA",
    "dest_lat": 38.5816,
    "dest_lng": -121.4944,
    "session_notes": "Great meeting today",
    "is_complete": true,
    "events": [
      {
        "id": "uuid",
        "type": "check_in",
        "ts_client": "2025-01-01T12:00:00Z",
        "ts_server": "2025-01-01T12:00:02Z",
        "lat": 38.5817,
        "lng": -121.4945,
        "location_flag": "granted",
        "notes": null
      },
      {
        "id": "uuid",
        "type": "check_out",
        "ts_client": "2025-01-01T13:04:00Z",
        "ts_server": "2025-01-01T13:04:03Z",
        "lat": 38.5818,
        "lng": -121.4946,
        "location_flag": "granted",
        "notes": null
      }
    ],
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T13:04:03Z"
  }
}
```

### Data Export

#### Export Logs
```http
POST /export/logs
Content-Type: application/json
Authorization: Bearer <token>

{
  "contact_id": "uuid",
  "session_ids": ["uuid1", "uuid2"],
  "format": "email",
  "email": {
    "to": ["recipient@example.com"],
    "subject": "My Activity Logs",
    "message": "Please find attached my activity logs."
  }
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "ok": true,
    "message": "Email sent successfully",
    "export_id": "exp_abc123"
  }
}
```

#### Export by Date Range
```http
POST /export/logs
Content-Type: application/json
Authorization: Bearer <token>

{
  "contact_id": "uuid",
  "filter": {
    "from": "2025-01-01",
    "to": "2025-01-31",
    "category": ["AA", "NA"]
  },
  "format": "pdf",
  "email": {
    "to": ["recipient@example.com"],
    "subject": "January Activity Logs"
  }
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "ok": true,
    "message": "PDF generated and emailed successfully",
    "export_id": "exp_xyz789",
    "pdf_url": "https://storage.verifiedcompliance.com/exports/exp_xyz789.pdf"
  }
}
```

### Public Share

#### Get Public Share
```http
GET /public/{public_token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "dest_name": "Downtown AA Meeting",
    "dest_address": "123 Main St, Sacramento CA",
    "check_in_ts": "2025-01-01T12:00:00Z",
    "check_out_ts": "2025-01-01T13:04:00Z",
    "duration_minutes": 64,
    "location_flag": "granted",
    "notes": "Great session",
    "map_url": "https://maps.googleapis.com/staticmap?center=38.5816,-121.4944&zoom=15&size=400x300&key=...",
    "qr_code_url": "https://storage.verifiedcompliance.com/qr/pub_xyz789.png",
    "created_at": "2025-01-01T13:04:05Z"
  }
}
```

### Admin Endpoints

#### Create Meeting (Admin)
```http
POST /admin/meetings
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "name": "New Downtown Meeting",
  "description": "Open meeting for all",
  "address": "789 Oak St, Sacramento CA 95814",
  "lat": 38.5820,
  "lng": -121.4950,
  "category": "AA",
  "timezone": "America/Los_Angeles",
  "start_time": "2025-01-01T19:00:00Z",
  "end_time": "2025-01-01T20:00:00Z"
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "meeting_id": "uuid",
    "name": "New Downtown Meeting",
    "address": "789 Oak St, Sacramento CA 95814",
    "lat": 38.5820,
    "lng": -121.4950,
    "category": "AA",
    "is_active": true,
    "created_at": "2025-01-01T12:00:00Z"
  },
  "message": "Meeting created successfully"
}
```

#### Import Meetings (Admin)
```http
POST /admin/meetings/import
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "csv_data": "base64_encoded_csv",
  "geocode_missing": true
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "imported": 45,
    "failed": 3,
    "errors": [
      {
        "row": 12,
        "reason": "Invalid timezone"
      }
    ]
  },
  "message": "Import completed"
}
```

#### Get Analytics (Admin)
```http
GET /admin/analytics?from=2025-01-01&to=2025-01-31
Authorization: Bearer <admin_token>
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "total_contacts": 1247,
    "total_sessions": 3891,
    "session_completion_rate": 87.3,
    "avg_duration_minutes": 58.4,
    "location_success_rate": 94.2,
    "location_denials": 226,
    "repeat_usage_avg": 3.1,
    "entry_source": {
      "qr": 42,
      "link": 38,
      "seo": 20
    },
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    }
  }
}
```

---

## Data Models

### Contact Model
```json
{
  "contact_id": "uuid",
  "email": "user@example.com",
  "phone": "+15555551234",
  "first_name": "John",
  "last_name": "Doe",
  "ghl_contact_id": "ghl_abc123",
  "consent_granted": true,
  "consent_timestamp": "2025-01-01T12:00:00Z",
  "notes": "Additional notes",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### Meeting Model
```json
{
  "id": "uuid",
  "name": "Downtown AA Meeting",
  "description": "Open meeting for all",
  "address": "123 Main St, Sacramento CA 95814",
  "lat": 38.5816,
  "lng": -121.4944,
  "start_time": "2025-01-01T19:00:00Z",
  "end_time": "2025-01-01T20:00:00Z",
  "is_active": true,
  "qr_code": "QR_ABC123",
  "category": "AA",
  "timezone": "America/Los_Angeles",
  "created_by": "uuid",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### Session Model
```json
{
  "session_id": "uuid",
  "contact_id": "uuid",
  "meeting_id": "uuid",
  "dest_name": "Downtown AA Meeting",
  "dest_address": "123 Main St, Sacramento CA",
  "dest_lat": 38.5816,
  "dest_lng": -121.4944,
  "session_notes": "Great meeting today",
  "is_complete": true,
  "events": [
    {
      "id": "uuid",
      "type": "check_in",
      "ts_client": "2025-01-01T12:00:00Z",
      "ts_server": "2025-01-01T12:00:02Z",
      "lat": 38.5817,
      "lng": -121.4945,
      "location_flag": "granted",
      "notes": null
    }
  ],
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T13:04:03Z"
}
```

### Session Event Model
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "type": "check_in",
  "ts_client": "2025-01-01T12:00:00Z",
  "ts_server": "2025-01-01T12:00:02Z",
  "lat": 38.5817,
  "lng": -121.4945,
  "location_flag": "granted",
  "notes": null,
  "created_at": "2025-01-01T12:00:02Z",
  "updated_at": "2025-01-01T12:00:02Z"
}
```

---

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **410 Gone**: Resource expired
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Codes
```json
{
  "VALIDATION_ERROR": "Request data validation failed",
  "AUTHENTICATION_REQUIRED": "Valid authentication required",
  "AUTHORIZATION_DENIED": "Insufficient permissions",
  "RESOURCE_NOT_FOUND": "Requested resource not found",
  "RESOURCE_EXPIRED": "Resource has expired",
  "RATE_LIMIT_EXCEEDED": "Too many requests",
  "LOCATION_VERIFICATION_FAILED": "GPS verification failed",
  "SESSION_EXPIRED": "Session has expired",
  "INVALID_TOKEN": "Token is invalid or expired",
  "EXTERNAL_SERVICE_ERROR": "External service unavailable",
  "DATABASE_ERROR": "Database operation failed",
  "INTERNAL_SERVER_ERROR": "Internal server error"
}
```

### Validation Errors
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "email": ["Invalid email format"],
      "phone": ["Phone number must be in E.164 format"],
      "consent_granted": ["This field is required"]
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Location Verification Errors
```json
{
  "success": false,
  "error": {
    "code": "LOCATION_VERIFICATION_FAILED",
    "message": "Location verification failed",
    "details": {
      "distance_meters": 250,
      "threshold_meters": 200,
      "user_lat": 38.5817,
      "user_lng": -121.4945,
      "dest_lat": 38.5816,
      "dest_lng": -121.4944
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Rules
```yaml
# Global rate limits
global: 1000 requests/hour
per_ip: 100 requests/minute
per_user: 500 requests/hour

# Endpoint-specific limits
auth_endpoints: 10 requests/minute
webhook_endpoints: 50 requests/minute
export_endpoints: 5 requests/minute
admin_endpoints: 200 requests/hour
```

### Rate Limit Exceeded Response
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_time": "2025-01-01T12:01:00Z"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## Webhooks

### Webhook Endpoint
```http
POST /webhooks/ghl
Content-Type: application/json
X-VC-Signature: sha256=abc123...
```

### Webhook Payload
```json
{
  "contact": {
    "email": "user@example.com",
    "phone": "+15555551234",
    "firstName": "John",
    "lastName": "Doe"
  },
  "session_id": "uuid",
  "event": "check_out",
  "check_in": {
    "timestamp": "2025-01-01T12:00:00Z",
    "lat": 38.5817,
    "lng": -121.4945
  },
  "check_out": {
    "timestamp": "2025-01-01T13:04:00Z",
    "lat": 38.5818,
    "lng": -121.4946
  },
  "duration_minutes": 64,
  "destination": "Downtown AA Meeting - 123 Main St",
  "notes": "Great session",
  "location_flag": "granted"
}
```

### Webhook Signature Verification
```python
import hmac
import hashlib
import base64

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected_signature}")
```

---

## API Versioning

### Version Strategy
- **Current Version**: v1
- **Version Header**: `API-Version: v1`
- **URL Versioning**: `/api/v1/`
- **Backward Compatibility**: 6 months minimum

### Version Deprecation
```http
API-Version: v1
X-API-Deprecated: true
X-API-Sunset: 2025-07-01T00:00:00Z
```

### Breaking Changes
- Removing fields from response
- Changing field types
- Renaming fields
- Changing HTTP status codes
- Adding required request fields

### Non-Breaking Changes
- Adding optional fields to request
- Adding new fields to response
- Adding new endpoints
- Bug fixes that don't change behavior

---

This comprehensive API design document provides detailed specifications for all endpoints, data models, error handling, and integration patterns for the Verified Compliance system. The API is designed to be RESTful, secure, and scalable while providing excellent developer experience for both backend and frontend teams.
