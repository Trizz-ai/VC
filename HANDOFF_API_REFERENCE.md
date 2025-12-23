# Verified Compliance™ — API Reference

## Complete API Documentation

---

## Base URL

| Environment | URL |
|-------------|-----|
| Local Development | `http://localhost:8000` |
| Production | `https://api.verifiedcompliance.com` |

## Authentication

All endpoints (except auth and public) require JWT authentication.

### Request Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Token Lifecycle

- Tokens expire after 30 minutes (configurable)
- Use refresh endpoint to get new token
- Store tokens securely (Flutter secure storage)

---

## API Endpoints

### Authentication

#### POST /api/v1/auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "phone": "+15305551212",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "consent_granted": true
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": "+15305551212",
  "first_name": "John",
  "last_name": "Doe",
  "consent_granted": true,
  "created_at": "2024-12-23T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `409 Conflict` - Email already exists

---

#### POST /api/v1/auth/login

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "contact": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing fields

---

#### GET /api/v1/auth/me

Get current authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": "+15305551212",
  "first_name": "John",
  "last_name": "Doe",
  "consent_granted": true,
  "is_active": true,
  "created_at": "2024-12-23T10:00:00Z"
}
```

---

### Contacts

#### GET /api/v1/contacts/{contact_id}

Get contact by ID.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": "+15305551212",
  "first_name": "John",
  "last_name": "Doe",
  "ghl_contact_id": "ghl_abc123",
  "consent_granted": true,
  "consent_timestamp": "2024-12-23T10:00:00Z",
  "is_active": true
}
```

---

#### PATCH /api/v1/contacts/{contact_id}

Update contact information.

**Request Body:**
```json
{
  "first_name": "Jonathan",
  "phone": "+15305551234"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": "+15305551234",
  "first_name": "Jonathan",
  "last_name": "Doe"
}
```

---

### Meetings

#### GET /api/v1/meetings/nearby

Find meetings near a location.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude (-90 to 90) |
| lng | float | Yes | Longitude (-180 to 180) |
| limit | int | No | Max results (default: 25) |
| radius | int | No | Search radius in meters (default: 25000) |

**Example Request:**
```
GET /api/v1/meetings/nearby?lat=38.5816&lng=-121.4944&limit=10
```

**Response (200 OK):**
```json
{
  "meetings": [
    {
      "id": "meeting-uuid-1",
      "name": "Downtown AA Meeting",
      "address": "123 Main St, Sacramento CA",
      "lat": 38.5816,
      "lng": -121.4944,
      "distance_meters": 150,
      "radius_meters": 100,
      "is_active": true
    },
    {
      "id": "meeting-uuid-2",
      "name": "Midtown NA Group",
      "address": "456 Oak Ave, Sacramento CA",
      "lat": 38.5750,
      "lng": -121.4800,
      "distance_meters": 850,
      "radius_meters": 100,
      "is_active": true
    }
  ],
  "total": 2,
  "user_location": {
    "lat": 38.5816,
    "lng": -121.4944
  }
}
```

---

#### GET /api/v1/meetings/search

Search meetings by name or address.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query (min 3 chars) |
| lat | float | No | User latitude for distance calculation |
| lng | float | No | User longitude for distance calculation |
| limit | int | No | Max results (default: 25) |

**Example Request:**
```
GET /api/v1/meetings/search?q=downtown&lat=38.5816&lng=-121.4944
```

**Response (200 OK):**
```json
{
  "meetings": [
    {
      "id": "meeting-uuid-1",
      "name": "Downtown AA Meeting",
      "address": "123 Main St, Sacramento CA",
      "lat": 38.5816,
      "lng": -121.4944,
      "distance_meters": 150
    }
  ],
  "query": "downtown",
  "total": 1
}
```

---

#### GET /api/v1/meetings/{meeting_id}

Get meeting details.

**Response (200 OK):**
```json
{
  "id": "meeting-uuid-1",
  "name": "Downtown AA Meeting",
  "description": "Open meeting, all welcome",
  "address": "123 Main St, Sacramento CA",
  "lat": 38.5816,
  "lng": -121.4944,
  "radius_meters": 100,
  "is_active": true,
  "created_at": "2024-12-01T00:00:00Z"
}
```

---

### Sessions

#### POST /api/v1/sessions

Create a new session (start tracking).

**Request Body:**
```json
{
  "meeting_id": "meeting-uuid-1",
  "notes": "Optional notes"
}
```

**Response (201 Created):**
```json
{
  "id": "session-uuid-1",
  "contact_id": "contact-uuid",
  "meeting_id": "meeting-uuid-1",
  "status": "active",
  "dest_name": "Downtown AA Meeting",
  "dest_address": "123 Main St, Sacramento CA",
  "dest_lat": 38.5816,
  "dest_lng": -121.4944,
  "session_notes": "Optional notes",
  "is_complete": false,
  "created_at": "2024-12-23T10:00:00Z"
}
```

---

#### POST /api/v1/sessions/{session_id}/check-in

Check in to a session.

**Request Body:**
```json
{
  "latitude": 38.5817,
  "longitude": -121.4945,
  "accuracy": 10.5,
  "altitude": 25.0,
  "timestamp": 1703322000000,
  "notes": "Arrived on time"
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "session_id": "session-uuid-1",
  "event_id": "event-uuid-1",
  "check_in_ts": "2024-12-23T10:00:02Z",
  "location_flag": "granted",
  "distance_meters": 15.5,
  "within_range": true
}
```

**Error Responses:**
- `400 Bad Request` - Location too far from meeting
- `404 Not Found` - Session not found
- `409 Conflict` - Already checked in

---

#### POST /api/v1/sessions/{session_id}/check-out

Check out of a session.

**Request Body:**
```json
{
  "latitude": 38.5818,
  "longitude": -121.4946,
  "accuracy": 12.0,
  "notes": "Great meeting"
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "session_id": "session-uuid-1",
  "check_out_ts": "2024-12-23T11:04:03Z",
  "duration_minutes": 64,
  "location_flag": "granted",
  "public_token": "pub_xyz789"
}
```

---

#### GET /api/v1/sessions

Get sessions for current user.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number (default: 1) |
| per_page | int | No | Items per page (default: 20) |
| status | string | No | Filter by status |

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "id": "session-uuid-1",
      "contact_id": "contact-uuid",
      "meeting_id": "meeting-uuid-1",
      "status": "completed",
      "dest_name": "Downtown AA Meeting",
      "dest_address": "123 Main St",
      "check_in_time": "2024-12-23T10:00:00Z",
      "check_out_time": "2024-12-23T11:04:00Z",
      "duration_minutes": 64,
      "session_notes": "Great meeting",
      "is_complete": true
    }
  ],
  "total": 47,
  "page": 1,
  "per_page": 20
}
```

---

#### GET /api/v1/sessions/{session_id}

Get session details with events.

**Response (200 OK):**
```json
{
  "session": {
    "id": "session-uuid-1",
    "status": "completed",
    "dest_name": "Downtown AA Meeting",
    "dest_address": "123 Main St",
    "check_in_time": "2024-12-23T10:00:00Z",
    "check_out_time": "2024-12-23T11:04:00Z"
  },
  "meeting": {
    "id": "meeting-uuid-1",
    "name": "Downtown AA Meeting",
    "address": "123 Main St, Sacramento CA"
  },
  "events": [
    {
      "id": "event-uuid-1",
      "type": "check_in",
      "timestamp": "2024-12-23T10:00:02Z",
      "lat": 38.5817,
      "lng": -121.4945,
      "accuracy": 10.5,
      "location_flag": "granted"
    },
    {
      "id": "event-uuid-2",
      "type": "check_out",
      "timestamp": "2024-12-23T11:04:03Z",
      "lat": 38.5818,
      "lng": -121.4946,
      "accuracy": 12.0,
      "location_flag": "granted"
    }
  ]
}
```

---

### Public Share

#### GET /api/v1/public/{public_token}

Get public session data (no authentication required).

**Response (200 OK):**
```json
{
  "session_id": "session-uuid-1",
  "dest_name": "Downtown AA Meeting",
  "dest_address": "123 Main St, Sacramento CA",
  "check_in_ts": "2024-12-23T10:00:00Z",
  "check_out_ts": "2024-12-23T11:04:00Z",
  "duration_minutes": 64,
  "location_flag": "granted",
  "notes": "Great meeting",
  "map_url": "https://maps.googleapis.com/...",
  "disclaimer": "This is a documentation record. Final determinations are made by your supervising professional."
}
```

---

### Admin Endpoints

*Requires admin authentication*

#### POST /api/v1/admin/meetings

Create a new meeting.

**Request Body:**
```json
{
  "name": "New Downtown Meeting",
  "address": "789 Oak St, Sacramento CA 95814",
  "lat": 38.5820,
  "lng": -121.4950,
  "radius_meters": 100,
  "description": "Open meeting"
}
```

---

#### GET /api/v1/admin/analytics

Get system analytics.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| from | date | Start date (YYYY-MM-DD) |
| to | date | End date (YYYY-MM-DD) |

**Response (200 OK):**
```json
{
  "total_contacts": 1247,
  "total_sessions": 3891,
  "session_completion_rate": 87.3,
  "avg_duration_minutes": 58.4,
  "location_success_rate": 94.2,
  "period": {
    "from": "2024-12-01",
    "to": "2024-12-23"
  }
}
```

---

### Offline Sync

#### POST /api/v1/offline/sync

Sync offline queued data.

**Request Body:**
```json
{
  "queued_items": [
    {
      "local_id": "local-uuid-1",
      "type": "check_in",
      "session_id": "session-uuid-1",
      "data": {
        "latitude": 38.5817,
        "longitude": -121.4945,
        "accuracy": 10.5,
        "device_timestamp": "2024-12-23T10:00:00Z"
      },
      "queued_at": "2024-12-23T10:00:00Z"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "synced": [
    {
      "local_id": "local-uuid-1",
      "server_id": "event-uuid-1",
      "status": "success"
    }
  ],
  "failed": [],
  "total_synced": 1,
  "total_failed": 0
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-12-23T10:00:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `CONFLICT` | 409 | Resource conflict (e.g., duplicate) |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Rate Limiting

| Endpoint Type | Limit |
|---------------|-------|
| Authentication | 10 requests/minute |
| Standard API | 100 requests/minute |
| Search | 30 requests/minute |
| Admin | 50 requests/minute |

Rate limit headers returned:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1703322060
```

---

## Webhooks (Outgoing)

### GoHighLevel Webhook

Triggered on session completion.

**Payload:**
```json
{
  "contact": {
    "email": "user@example.com",
    "phone": "+15305551212",
    "firstName": "John",
    "lastName": "Doe"
  },
  "session_id": "session-uuid-1",
  "check_in": {
    "timestamp": "2024-12-23T10:00:00Z",
    "lat": 38.5817,
    "lng": -121.4945
  },
  "check_out": {
    "timestamp": "2024-12-23T11:04:00Z",
    "lat": 38.5818,
    "lng": -121.4946
  },
  "duration_minutes": 64,
  "destination": "Downtown AA Meeting - 123 Main St",
  "notes": "Great meeting",
  "location_flag": "granted"
}
```

**Headers:**
```http
X-VC-Signature: sha256=<hmac_signature>
Content-Type: application/json
```

---

## Testing the API

### Using Swagger UI

1. Start backend: `uvicorn app.main:app --reload`
2. Open: http://localhost:8000/docs
3. Click "Authorize" and enter JWT token
4. Test any endpoint directly

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Use token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

### Using Postman

1. Import OpenAPI spec from http://localhost:8000/openapi.json
2. Configure environment variables for base URL and token
3. Run requests

---

## API Versioning

Current version: **v1**

All endpoints are prefixed with `/api/v1/`

Future versions will use `/api/v2/` etc.

Deprecation notices will be communicated via:
- `Deprecation` header in responses
- Documentation updates
- Migration guides

---

**For interactive API testing, use the Swagger UI at `/docs` when the backend is running.**

