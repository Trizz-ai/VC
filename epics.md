# Verified Compliance App - Development Breakdown
## Flutter Frontend + Python (FastAPI) Backend

---

## EPIC 1: User Onboarding & Contact Management

### User Story 1.1: First-Time User Consent
**As a** new user  
**I want to** provide my contact information and grant GPS consent  
**So that** I can start tracking my attendance

**Acceptance Criteria:**
- [ ] Splash screen displays app name and logo
- [ ] Consent screen explains GPS tracking clearly with plain language
- [ ] Form collects: email, phone, first name, last name
- [ ] Checkbox for "I consent to GPS tracking" is required
- [ ] Email validation (format check)
- [ ] Phone validation (E.164 format preferred)
- [ ] Submit button disabled until all required fields valid
- [ ] Success creates contact record in Postgres with `consent_granted=true`
- [ ] Contact is upserted to GHL via API (email as primary key, phone as fallback)
- [ ] `ghl_contact_id` stored in local contact record
- [ ] Error handling: duplicate email shows "Account exists" message
- [ ] On success, navigate to Meeting Finder screen

**API Endpoint:** `POST /api/v1/contacts`
```json
Request: {
  "email": "user@example.com",
  "phone": "+15305551212",
  "given_name": "Alex",
  "family_name": "Patient",
  "consent_granted": true
}
Response: {
  "contact_id": "uuid",
  "ghl_contact_id": "ghl_abc123"
}
```

---

### User Story 1.2: Return User Recognition
**As a** returning user  
**I want to** be automatically recognized  
**So that** I don't have to re-enter my information

**Acceptance Criteria:**
- [ ] App stores `contact_id` in Flutter secure storage after first login
- [ ] On app launch, check for stored `contact_id`
- [ ] If found, validate with backend: `GET /api/v1/contacts/{contact_id}`
- [ ] If valid, skip onboarding and go directly to Meeting Finder
- [ ] If invalid (404), clear storage and show onboarding
- [ ] "Sign Out" option in settings clears stored `contact_id`

**API Endpoint:** `GET /api/v1/contacts/{contact_id}`
```json
Response: {
  "contact_id": "uuid",
  "email": "user@example.com",
  "given_name": "Alex",
  "consent_granted": true
}
```

---

## EPIC 2: Meeting Discovery & Selection

### User Story 2.1: Find Nearby Meetings via GPS
**As a** user  
**I want to** see a list of nearby meetings based on my current location  
**So that** I can choose where to check in

**Acceptance Criteria:**
- [ ] On Meeting Finder screen load, request GPS permission
- [ ] Show permission rationale if denied previously
- [ ] Display loading indicator while fetching GPS coordinates
- [ ] GPS request uses high accuracy mode with 15-second timeout
- [ ] On GPS success, call `GET /api/v1/meetings/nearby?lat={lat}&lng={lng}&limit=25`
- [ ] Display meetings list sorted by distance (closest first)
- [ ] Each list item shows: meeting name, address, distance (miles/km based on locale), category badge
- [ ] Distance updates in real-time if user location changes significantly (>100m)
- [ ] Pull-to-refresh reloads meeting list
- [ ] Empty state: "No meetings found within 25 miles. Try custom destination?"
- [ ] Error state: GPS disabled shows "Enable Location Services" with settings deep link
- [ ] Tapping a meeting navigates to Session Start screen with pre-filled destination

**API Endpoint:** `GET /api/v1/meetings/nearby`
```json
Query Params: { lat, lng, limit=25, category=null }
Response: {
  "meetings": [
    {
      "id": "uuid",
      "name": "Downtown AA Meeting",
      "address": "123 Main St, Sacramento CA",
      "lat": 38.5816,
      "lng": -121.4944,
      "distance_meters": 450,
      "category": "AA",
      "timezone": "America/Los_Angeles"
    }
  ]
}
```

---

### User Story 2.2: Search Meetings by Name/Address
**As a** user  
**I want to** search for meetings by name or address  
**So that** I can find a specific meeting quickly

**Acceptance Criteria:**
- [ ] Search bar visible at top of Meeting Finder screen
- [ ] Search is debounced (300ms delay after typing stops)
- [ ] Calls `GET /api/v1/meetings/search?q={query}&lat={lat}&lng={lng}`
- [ ] Results show matches in name or address fields
- [ ] Results still sorted by distance if GPS available
- [ ] Minimum 3 characters required to trigger search
- [ ] Clear button (X) resets to nearby meetings list
- [ ] Search works offline with cached meetings (if previously loaded)

**API Endpoint:** `GET /api/v1/meetings/search`
```json
Query Params: { q, lat?, lng?, limit=25 }
Response: { meetings: [...] }
```

---

### User Story 2.3: Log Custom Destination
**As a** user  
**I want to** log attendance at a custom destination (gym, church, etc.)  
**So that** I can track activity beyond catalog meetings

**Acceptance Criteria:**
- [ ] Meeting Finder has "Custom Destination" button
- [ ] Modal opens with fields: destination name (required), address (optional)
- [ ] If address provided, backend geocodes and stores lat/lng
- [ ] If no address, uses current GPS as destination coordinates
- [ ] Calls `POST /api/v1/sessions/start` with `meeting_id=null` and `dest_*` fields
- [ ] Custom destinations saved for quick re-selection (last 10 stored locally)
- [ ] Recent custom destinations appear in separate section below meetings list

**API Endpoint:** `POST /api/v1/sessions/start`
```json
Request: {
  "contact_id": "uuid",
  "meeting_id": null,
  "dest_name": "Planet Fitness",
  "dest_address": "456 Elm St",
  "dest_lat": 38.5820,
  "dest_lng": -121.4950,
  "source": "custom",
  "category": "Gym"
}
Response: {
  "session_id": "uuid",
  "session_token": "short_token_abc123",
  "expires_at": "2025-10-01T10:30:00Z"
}
```

---

## EPIC 3: Check-In/Check-Out Flow

### User Story 3.1: Start Session & Check-In
**As a** user  
**I want to** check in at my destination  
**So that** my arrival is recorded with GPS verification

**Acceptance Criteria:**
- [ ] Session screen shows destination name, address, map preview
- [ ] "Check In" button is large (min 56dp height) and prominently displayed
- [ ] Tapping Check In requests current GPS location
- [ ] Loading state shows "Verifying location..." with spinner
- [ ] Captures: timestamp (ISO8601), lat, lng, accuracy
- [ ] Calls `POST /api/v1/sessions/{session_id}/check-in`
- [ ] Backend calculates distance from dest_lat/lng using Haversine
- [ ] If distance >200m, backend sets `location_flag='denied'`
- [ ] Success shows green checkmark with "Checked In at [time]"
- [ ] Check-In button is hidden after success
- [ ] Check-Out button becomes visible
- [ ] Session duration timer starts (shows elapsed time: "00:05:23")
- [ ] Error handling: GPS timeout shows retry option, network error shows offline message

**API Endpoint:** `POST /api/v1/sessions/{session_id}/check-in`
```json
Request: {
  "session_token": "short_token",
  "coords": { "lat": 38.5817, "lng": -121.4945, "accuracy": 12 },
  "client_ts": "2025-10-01T10:00:00Z"
}
Response: {
  "ok": true,
  "check_in_ts": "2025-10-01T10:00:02Z",
  "location_flag": "ok"
}
```

---

### User Story 3.2: Add/Edit Session Notes
**As a** user  
**I want to** add notes to my session  
**So that** I can document details about my visit

**Acceptance Criteria:**
- [ ] "Add Notes" button visible on Session screen after Check-In
- [ ] Tapping opens modal with text field (multiline, max 500 chars)
- [ ] Character counter displayed
- [ ] Auto-saves on dismissal via `PATCH /api/v1/sessions/{session_id}/notes`
- [ ] Notes editable during active session
- [ ] Notes remain editable for 5 minutes after Check-Out
- [ ] After 5-minute window, notes become read-only
- [ ] Notes preview shown on Session screen (first 50 chars + "..." if truncated)
- [ ] Offline: notes cached locally and synced when online

**API Endpoint:** `PATCH /api/v1/sessions/{session_id}/notes`
```json
Request: {
  "session_token": "short_token",
  "notes": "Today I worked out chest and back",
  "client_ts": "2025-10-01T10:15:00Z"
}
Response: { "ok": true }
```

---

### User Story 3.3: Check-Out & View Duration
**As a** user  
**I want to** check out when I leave  
**So that** my total attendance duration is calculated

**Acceptance Criteria:**
- [ ] "Check Out" button visible after Check-In
- [ ] Tapping Check Out requests current GPS location
- [ ] Captures: timestamp, lat, lng, accuracy
- [ ] Calls `POST /api/v1/sessions/{session_id}/check-out`
- [ ] Backend calculates duration: `check_out_ts - check_in_ts`
- [ ] Backend verifies Check-Out location (distance check, same 200m threshold)
- [ ] Success shows summary card:
  - Destination name
  - Check-In time
  - Check-Out time
  - Duration (hours:minutes)
  - Location status badge (Verified / Flagged)
  - Notes preview
- [ ] "View Shareable Log" button navigates to Public Share screen
- [ ] "Back to Dashboard" button navigates to Activity Logs
- [ ] GHL webhook triggered with full session data, tags, and contact fields updated

**API Endpoint:** `POST /api/v1/sessions/{session_id}/check-out`
```json
Request: {
  "session_token": "short_token",
  "coords": { "lat": 38.5818, "lng": -121.4946, "accuracy": 15 },
  "client_ts": "2025-10-01T11:04:00Z"
}
Response: {
  "ok": true,
  "check_out_ts": "2025-10-01T11:04:03Z",
  "duration_minutes": 64,
  "location_flag": "ok",
  "public_token": "pub_xyz789"
}
```

---

### User Story 3.4: Session Expiration
**As a** user  
**I want** my session to expire if I don't check in within 15 minutes  
**So that** stale sessions don't clutter my log

**Acceptance Criteria:**
- [ ] Backend sets session `expires_at` to 15 minutes after creation
- [ ] Polling: Flutter app calls `GET /api/v1/sessions/{session_id}/status` every 60 seconds
- [ ] If backend returns `status=expired`, show modal: "Session expired. Start a new one?"
- [ ] Expired sessions not shown in Activity Logs unless Check-In occurred
- [ ] Cleanup job: backend marks sessions as expired if not checked in after TTL

**API Endpoint:** `GET /api/v1/sessions/{session_id}/status`
```json
Response: {
  "status": "active" | "expired" | "complete",
  "expires_at": "2025-10-01T10:15:00Z"
}
```

---

## EPIC 4: Activity Logs Dashboard

### User Story 4.1: View All Activity Logs
**As a** user  
**I want to** see a list of all my past sessions  
**So that** I can review my attendance history

**Acceptance Criteria:**
- [ ] Dashboard shows paginated list of sessions (20 per page)
- [ ] Each log card displays:
  - Date (formatted: "Sep 28, 2025")
  - Destination name
  - Address (truncated)
  - Check-In time
  - Check-Out time
  - Duration
  - Location status badge (Verified / Flagged)
  - Notes preview (first 50 chars)
  - Checkbox for selection
- [ ] Default sort: most recent first
- [ ] Pull-to-refresh reloads first page
- [ ] Infinite scroll loads next page automatically
- [ ] Empty state: "No activity logs yet. Start your first session!"
- [ ] Tapping a log expands details view

**API Endpoint:** `GET /api/v1/sessions`
```json
Query Params: { contact_id, page=1, per_page=20, range=null, category=null, query=null }
Response: {
  "sessions": [
    {
      "session_id": "uuid",
      "dest_name": "Downtown AA Meeting",
      "dest_address": "123 Main St",
      "check_in_ts": "2025-09-28T10:00:00Z",
      "check_out_ts": "2025-09-28T11:04:00Z",
      "duration_minutes": 64,
      "location_flag": "ok",
      "notes": "Great meeting today",
      "category": "AA",
      "public_token": "pub_xyz"
    }
  ],
  "total": 47,
  "page": 1,
  "per_page": 20
}
```

---

### User Story 4.2: Search Logs by Keyword
**As a** user  
**I want to** search my logs by destination name, address, or notes  
**So that** I can quickly find specific sessions

**Acceptance Criteria:**
- [ ] Search bar at top of Dashboard
- [ ] Debounced search (300ms)
- [ ] Searches across: `dest_name`, `dest_address`, `session_notes`
- [ ] Minimum 3 characters to trigger
- [ ] Results update list in-place
- [ ] Clear button resets to full list
- [ ] Works with other filters (date range, category)

**API Endpoint:** Same as 4.1, with `query` param populated

---

### User Story 4.3: Filter Logs by Date Range
**As a** user  
**I want to** filter logs by date range  
**So that** I can view specific time periods

**Acceptance Criteria:**
- [ ] Filter chips: "Last 7 days", "Last 30 days", "Custom"
- [ ] Default: no filter (show all)
- [ ] Custom opens date range picker (From/To dates)
- [ ] Apply button triggers API call with `range` param
- [ ] Active filter shown with dismiss (X) icon
- [ ] Clearing filter resets to full list

**API Endpoint:** Same as 4.1, with `range=7d|30d|custom&from=YYYY-MM-DD&to=YYYY-MM-DD`

---

### User Story 4.4: Filter Logs by Category
**As a** user  
**I want to** filter logs by category (AA, Gym, Church, etc.)  
**So that** I can view specific types of activities

**Acceptance Criteria:**
- [ ] Category filter dropdown/chips (multi-select)
- [ ] Categories: AA, NA, Gym, Church, School, Custom, (dynamic from data)
- [ ] Selecting applies filter immediately
- [ ] Shows count per category as badge
- [ ] "Clear" button removes all category filters
- [ ] Works with date range and search filters

**API Endpoint:** Same as 4.1, with `category=AA,Gym`

---

### User Story 4.5: Group Logs by Destination
**As a** user  
**I want to** group logs by destination  
**So that** I can see all visits to the same place together

**Acceptance Criteria:**
- [ ] Toggle button: "Group by Destination"
- [ ] When enabled, logs grouped with destination as header
- [ ] Shows visit count per destination
- [ ] Collapsible groups (expand/collapse)
- [ ] Each group sorted by date descending
- [ ] Toggle persists in local storage

**API Endpoint:** Same as 4.1, with `group_by=destination`

---

### User Story 4.6: Select Multiple Logs for Actions
**As a** user  
**I want to** select one or multiple logs  
**So that** I can email or print them together

**Acceptance Criteria:**
- [ ] Each log has a checkbox
- [ ] "Select All" button in app bar selects all visible logs
- [ ] "Clear Selection" button deselects all
- [ ] Selection count shown in sticky footer bar
- [ ] Footer shows: "[X] selected | Email | Print | Cancel"
- [ ] Cancel clears selection and hides footer
- [ ] Selection persists when scrolling (state management)

---

### User Story 4.7: Email Selected Logs
**As a** user  
**I want to** email selected logs  
**So that** I can share my attendance with others

**Acceptance Criteria:**
- [ ] Tapping "Email" opens modal
- [ ] Modal has fields: To (email), Subject (pre-filled), Message (optional)
- [ ] Preview shows count: "X logs will be emailed"
- [ ] "Send" button calls `POST /api/v1/export/logs`
- [ ] Backend generates PDF with:
  - Header: "Activity Logs for [Name]"
  - Each log: Date, Destination, Address, Check-In, Check-Out, Duration, Location Status, Notes
  - Footer: "Generated on [date] via Verified Compliance"
- [ ] Backend sends email via SMTP or GHL email workflow
- [ ] Success message: "Logs emailed to [email]"
- [ ] Error handling: invalid email, network failure

**API Endpoint:** `POST /api/v1/export/logs`
```json
Request: {
  "contact_id": "uuid",
  "session_ids": ["uuid1", "uuid2"],
  "format": "email",
  "email": {
    "to": ["recipient@example.com"],
    "subject": "My Activity Logs",
    "message": "Please find attached."
  }
}
Response: { "ok": true, "message": "Email sent successfully" }
```

---

### User Story 4.8: Print Selected Logs
**As a** user  
**I want to** print selected logs  
**So that** I can have a physical copy

**Acceptance Criteria:**
- [ ] Tapping "Print" generates print-friendly HTML view
- [ ] Opens in browser print dialog (iOS/Android)
- [ ] Layout: portrait, clean formatting, page breaks between logs
- [ ] Includes same content as email export
- [ ] Option to "Save as PDF" (native platform behavior)

**API Endpoint:** `POST /api/v1/export/logs`
```json
Request: { ..., "format": "pdf" }
Response: { "ok": true, "pdf_url": "https://..." }
```

---

### User Story 4.9: Email Logs by Date Range
**As a** user  
**I want to** email all logs within a date range  
**So that** I don't have to manually select them

**Acceptance Criteria:**
- [ ] Toolbar button: "Email by Date"
- [ ] Opens modal with date picker (From/To)
- [ ] Optional: category filter
- [ ] Preview: "X logs match this range"
- [ ] Same email flow as 4.7
- [ ] Backend uses filter instead of session_ids

**API Endpoint:** `POST /api/v1/export/logs`
```json
Request: {
  "contact_id": "uuid",
  "filter": {
    "from": "2025-09-01",
    "to": "2025-09-30",
    "category": ["Gym"]
  },
  "format": "email",
  "email": { ... }
}
```

---

## EPIC 5: Public Share Page

### User Story 5.1: View Public Shareable Log
**As a** user  
**I want to** view a public shareable version of my session  
**So that** I can verify what others will see

**Acceptance Criteria:**
- [ ] After Check-Out, "View Shareable Log" button navigates to `/share/{public_token}`
- [ ] Public page shows:
  - "Verified Activity Log" header
  - Destination name and address
  - Static map image (centered on destination)
  - Check-In timestamp (formatted)
  - Check-Out timestamp (formatted)
  - Duration (hours:minutes)
  - Location status badge
  - Notes (if present)
  - QR code linking to this page
  - Disclaimer: "This is voluntary tracking, not court-admissible"
- [ ] Page accessible without authentication
- [ ] Share button opens native share sheet (copy link, SMS, email, etc.)
- [ ] "Back to Dashboard" button (only if logged in)

**API Endpoint:** `GET /api/v1/public/{public_token}`
```json
Response: {
  "session_id": "uuid",
  "dest_name": "Downtown AA Meeting",
  "dest_address": "123 Main St",
  "check_in_ts": "2025-10-01T10:00:00Z",
  "check_out_ts": "2025-10-01T11:04:00Z",
  "duration_minutes": 64,
  "location_flag": "ok",
  "notes": "Great session",
  "map_url": "https://maps.googleapis.com/...",
  "created_at": "2025-10-01T11:04:05Z"
}
```

---

### User Story 5.2: Generate QR Code for Public Log
**As a** user  
**I want** a QR code for my public log  
**So that** I can easily share it offline

**Acceptance Criteria:**
- [ ] QR code generated on public share page
- [ ] Encodes: `https://myverifiedcompliance.com/share/{public_token}`
- [ ] Tappable to enlarge (full-screen modal)
- [ ] "Save Image" button downloads QR as PNG
- [ ] QR works when scanned by any camera app

---

## EPIC 6: GHL (GoHighLevel) Integration

### User Story 6.1: Sync Contact on First Session
**As a** system  
**I want to** create/update contacts in GHL  
**So that** CRM records are automatically maintained

**Acceptance Criteria:**
- [ ] On contact creation, backend calls GHL Contacts API
- [ ] Upsert logic: search by email → update; else search by phone → update; else create new
- [ ] Store `ghl_contact_id` in local `contacts.ghl_contact_id`
- [ ] Handle API errors gracefully (retry with exponential backoff)
- [ ] Log all GHL API calls in `webhook_logs` table

**GHL API:** `POST /contacts/upsert`
```json
Request: {
  "email": "user@example.com",
  "phone": "+15305551212",
  "firstName": "Alex",
  "lastName": "Patient"
}
Response: { "contact": { "id": "ghl_abc123" } }
```

---

### User Story 6.2: Update Custom Fields on Check-Out
**As a** system  
**I want to** update GHL custom fields with session data  
**So that** contact records reflect latest activity

**Acceptance Criteria:**
- [ ] On Check-Out, update GHL contact with:
  - `VC: Last Check-In Timestamp`
  - `VC: Last Check-In Lat`
  - `VC: Last Check-In Lng`
  - `VC: Last Check-Out Timestamp`
  - `VC: Last Check-Out Lat`
  - `VC: Last Check-Out Lng`
  - `VC: Last Duration (min)`
  - `VC: Destination`
  - `VC: Session ID`
  - `VC: Consent Granted`
- [ ] Fields created in GHL account during setup
- [ ] Update via `PUT /contacts/{ghl_contact_id}/customFields`

---

### User Story 6.3: Add Tags on Check-In/Check-Out
**As a** system  
**I want to** add tags to GHL contacts  
**So that** workflows can be triggered based on activity

**Acceptance Criteria:**
- [ ] On Check-In: add tag `vc_checked_in`
- [ ] On Check-Out: add tags `vc_checked_out` and remove `vc_checked_in`
- [ ] If location flagged: add tag `vc_location_denied`
- [ ] Tags created in GHL account during setup
- [ ] Update via `POST /contacts/{ghl_contact_id}/tags`

---

### User Story 6.4: Send Webhook with Full Session Data
**As a** system  
**I want to** send session data to GHL via webhook  
**So that** custom workflows can process the information

**Acceptance Criteria:**
- [ ] On Check-Out, POST to GHL webhook URL (configured in env)
- [ ] Payload includes:
  - contact info
  - session timestamps (CI/CO)
  - coordinates (CI/CO)
  - duration
  - destination
  - notes
  - location_flag
- [ ] Payload signed with HMAC-SHA256
- [ ] Header: `X-VC-Signature: sha256={hash}`
- [ ] GHL workflow validates signature before processing
- [ ] Log webhook attempt in `webhook_logs` (status, response)
- [ ] Retry on failure (3 attempts with exponential backoff)

**Webhook Payload:**
```json
{
  "contact": {
    "email": "user@example.com",
    "phone": "+15305551212",
    "firstName": "Alex",
    "lastName": "Patient"
  },
  "session_id": "uuid",
  "check_in": {
    "timestamp": "2025-10-01T10:00:00Z",
    "lat": 38.5817,
    "lng": -121.4945
  },
  "check_out": {
    "timestamp": "2025-10-01T11:04:00Z",
    "lat": 38.5818,
    "lng": -121.4946
  },
  "duration_minutes": 64,
  "destination": "Downtown AA Meeting - 123 Main St",
  "notes": "Great session",
  "location_flag": "ok",
  "hmac": "sha256=abc123..."
}
```

---

### User Story 6.5: Add Note to GHL Contact Timeline
**As a** system  
**I want to** add a note to the GHL contact timeline  
**So that** staff can see session details in CRM

**Acceptance Criteria:**
- [ ] On Check-Out, create note via `POST /contacts/{ghl_contact_id}/notes`
- [ ] Note body format:
```
VC Session {session_id}
Check-In: {timestamp} @ ({lat}, {lng})
Check-Out: {timestamp} @ ({lat}, {lng})
Duration: {minutes} min
Destination: {name} - {address}
Notes: {session_notes}
Location Status: {flag}
```
- [ ] Note timestamp matches Check-Out time
- [ ] Error handling: if note fails, log but don't block Check-Out

---

## EPIC 7: Security & Privacy

### User Story 7.1: Secure Session Tokens
**As a** system  
**I want** session tokens to be short-lived and secure  
**So that** unauthorized access is prevented

**Acceptance Criteria:**
- [ ] Tokens: 128-bit random, base62-encoded
- [ ] TTL: 15 minutes from session creation
- [ ] Backend validates token on every API call
- [ ] Expired tokens return 410 Gone
- [ ] Invalid tokens return 404 Not Found
- [ ] Tokens stored hashed in database (SHA256)
- [ ] Public tokens separate from session tokens

---

### User Story 7.2: HTTPS & Transport Security
**As a** system  
**I want** all communication encrypted  
**So that** user data is protected in transit

**Acceptance Criteria:**
- [ ] Backend enforces HTTPS only (redirect HTTP → HTTPS)
- [ ] HSTS header set: `Strict-Transport-Security: max-age=31536000`
- [ ] Flutter app uses `https://` URLs only
- [ ] Certificate pinning in Flutter (optional, recommended)
- [ ] API responses include: `X-Content-Type-Options: nosniff`

---

### User Story 7.3: HMAC Webhook Signing
**As a** system  
**I want** webhooks signed with HMAC  
**So that** GHL can verify requests are authentic

**Acceptance Criteria:**
- [ ] Webhook secret stored in env: `HMAC_SECRET`
- [ ] Payload signed: `HMAC-SHA256(secret, payload)`
- [ ] Signature sent in header: `X-VC-Signature: sha256={hex}`
- [ ] GHL workflow validates signature before processing
- [ ] Mismatched signatures rejected (log attempt)

---

### User Story 7.4: No Background Tracking
**As a** user  
**I want** GPS only captured during Check-In/Check-Out  
**So that** my privacy is respected

**Acceptance Criteria:**
- [ ] GPS requested only when user taps Check-In or Check-Out
- [ ] No background location tracking (no `always` permission)
- [ ] Flutter: use `geolocator` with `whenInUse` permission
- [ ] Clear messaging: "Location used only during check-in/out"
- [ ] Location services can be disabled between sessions

---

### User Story 7.5: Data Minimization & Retention
**As a** system  
**I want to** collect only necessary data  
**So that** user privacy is maximized

**Acceptance Criteria:**
- [ ] Collect: name, email, phone, GPS coords, timestamps, notes
- [ ] Do NOT collect: device ID, IP address (except in logs), browsing history
- [ ] Session logs retained indefinitely (user-controlled deletion in future)
- [ ] Expired/incomplete sessions auto-deleted after 30 days
- [ ] User can request data export (future)

---

## EPIC 8: Offline Support & Error Handling

### User Story 8.1: Offline Mode Detection
**As a** user  
**I want** the app to detect when I'm offline  
**So that** I'm informed and can retry later

**Acceptance Criteria:**
- [ ] App detects network connectivity (Flutter `connectivity_plus`)
- [ ] Banner shown at top: "You're offline. Some features unavailable."
- [ ] API calls queued when offline
- [ ] Auto-retry when connection restored
- [ ] Offline indicator on Dashboard

---

### User Story 8.2: Offline Check-In/Check-Out Queuing
**As a** user  
**I want** Check-In/Check-Out to work offline  
**So that** I don't lose data if network is unavailable

**Acceptance Criteria:**
- [ ] Check-In captured locally with timestamp and GPS
- [ ] Stored in local SQLite database
- [ ] Banner: "Check-In saved locally. Will sync when online."
- [ ] Background sync attempts when network restored
- [ ] Synced events marked with checkmark icon
- [ ] Failed syncs retried with exponential backoff (max 3 attempts)
- [ ] User can manually retry from Dashboard

---

### User Story 8.3: GPS Error Handling
**As a** user  
**I want** clear guidance when GPS fails  
**So that** I know how to fix the issue

**Acceptance Criteria:**
- [ ] GPS timeout (>15 seconds): "Location taking too long. Try moving to an open area."
- [ ] GPS permission denied: "Location access required. Enable in Settings?" with deep link button
- [ ] GPS disabled: "Turn on Location Services to continue" with Settings button
- [ ] GPS low accuracy (>50m): Warning: "Location accuracy is low. Move to open area for better signal."
- [ ] Retry button on all GPS errors
- [ ] Error logged with context (permission status, accuracy, timeout reason)

---

### User Story 8.4: API Error Handling
**As a** user  
**I want** meaningful error messages when API calls fail  
**So that** I understand what went wrong

**Acceptance Criteria:**
- [ ] Network timeout: "Request timed out. Check your connection and try again."
- [ ] 400 Bad Request: Parse error message from API and display
- [ ] 401 Unauthorized: "Session expired. Please sign in again."
- [ ] 404 Not Found: "Resource not found. Please refresh."
- [ ] 500 Server Error: "Something went wrong. Please try again later."
- [ ] Rate limiting (429): "Too many requests. Please wait and try again."
- [ ] All errors logged with request context for debugging
- [ ] Generic fallback: "An error occurred. Please try again."
- [ ] Retry button on transient errors (timeout, 5xx)

---

## EPIC 9: Admin & Meeting Management

### User Story 9.1: CSV Meeting Import (Admin)
**As an** administrator  
**I want to** bulk import meetings from CSV  
**So that** I can populate the meeting catalog quickly

**Acceptance Criteria:**
- [ ] Admin endpoint: `POST /api/v1/admin/meetings/import`
- [ ] Protected by Bearer token authentication
- [ ] IP allowlist configured in env
- [ ] CSV format: `name, address, lat, lng, category, timezone, active`
- [ ] If lat/lng missing, backend geocodes address (Google Maps API)
- [ ] Validates: required fields, lat/lng bounds, valid timezone
- [ ] Returns: `{imported: 45, failed: 3, errors: [...]}`
- [ ] Failed rows logged with reason
- [ ] Duplicate detection: skip if same name + address exists
- [ ] Bulk insert optimized (batch 100 records)

**API Endpoint:** `POST /api/v1/admin/meetings/import`
```json
Request: {
  "csv_data": "base64_encoded_csv",
  "geocode_missing": true
}
Response: {
  "imported": 45,
  "failed": 3,
  "errors": [
    { "row": 12, "reason": "Invalid timezone" }
  ]
}
```

---

### User Story 9.2: Manual Meeting Creation (Admin)
**As an** administrator  
**I want to** manually add a single meeting  
**So that** I can update the catalog as needed

**Acceptance Criteria:**
- [ ] Admin endpoint: `POST /api/v1/admin/meetings`
- [ ] Required fields: name, address, category
- [ ] Optional: lat, lng (geocoded if missing), timezone (inferred if missing)
- [ ] Validation: address format, lat/lng bounds
- [ ] Returns created meeting with ID
- [ ] Audit log: admin_user, action, timestamp

**API Endpoint:** `POST /api/v1/admin/meetings`
```json
Request: {
  "name": "New Downtown Meeting",
  "address": "789 Oak St, Sacramento CA 95814",
  "category": "AA",
  "timezone": "America/Los_Angeles"
}
Response: {
  "meeting_id": "uuid",
  "lat": 38.5820,
  "lng": -121.4950
}
```

---

### User Story 9.3: Meeting Update/Deactivation (Admin)
**As an** administrator  
**I want to** update or deactivate meetings  
**So that** outdated information is removed

**Acceptance Criteria:**
- [ ] Admin endpoint: `PATCH /api/v1/admin/meetings/{meeting_id}`
- [ ] Can update: name, address, lat, lng, category, active status
- [ ] Setting `active=false` hides from public search but preserves historical data
- [ ] Sessions linked to deactivated meetings still display correctly
- [ ] Audit log: changes tracked with before/after values

**API Endpoint:** `PATCH /api/v1/admin/meetings/{meeting_id}`
```json
Request: {
  "active": false,
  "address": "Updated address"
}
Response: { "ok": true }
```

---

## EPIC 10: Analytics & KPIs

### User Story 10.1: Dashboard Analytics (Admin)
**As an** administrator  
**I want to** view key metrics in a dashboard  
**So that** I can monitor app health and usage

**Acceptance Criteria:**
- [ ] Admin dashboard at `/admin/analytics` (web UI or API)
- [ ] Metrics displayed:
  - Total contacts created
  - Total sessions (started, completed)
  - Session completion rate (%)
  - Average session duration (minutes)
  - Location verification success rate (%)
  - Location denials count
  - Repeat usage per contact (avg sessions per user)
  - Entry source breakdown (QR, Link, SEO %)
- [ ] Date range selector: Last 7/30/90 days, Custom
- [ ] Export to CSV button
- [ ] Real-time updates (refresh every 60s)

**API Endpoint:** `GET /api/v1/admin/analytics`
```json
Query Params: { from, to }
Response: {
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
  }
}
```

---

### User Story 10.2: Weekly KPI Report Generation
**As an** administrator  
**I want** automated weekly KPI reports  
**So that** I can track trends over time

**Acceptance Criteria:**
- [ ] Scheduled job runs every Monday at 9 AM
- [ ] Generates report for previous 7 days
- [ ] Report includes all metrics from 10.1
- [ ] Comparison to previous week (% change)
- [ ] Stored in database: `kpi_reports` table
- [ ] CSV export available via API
- [ ] Optional: email report to admin list

**API Endpoint:** `GET /api/v1/admin/reports/weekly`
```json
Query Params: { week_start_date }
Response: {
  "week_start": "2025-09-22",
  "week_end": "2025-09-28",
  "metrics": { ... },
  "comparison": {
    "total_contacts": "+12%",
    "session_completion_rate": "-2.1%"
  }
}
```

---

### User Story 10.3: GHL KPI Extraction
**As an** administrator  
**I want** KPIs extractable from GHL  
**So that** non-technical staff can run reports

**Acceptance Criteria:**
- [ ] GHL Smart Lists created for each KPI:
  - "VC: All Contacts" (filter: has VC Session ID field)
  - "VC: Checked In Today" (tag: vc_checked_in, date filter)
  - "VC: Location Denied" (tag: vc_location_denied)
- [ ] GHL Custom Reports configured:
  - Average session duration (from VC: Last Duration field)
  - Session completion rate (contacts with both CI and CO tags)
- [ ] Documentation: step-by-step guide for running reports in GHL
- [ ] Export templates: CSV format with predefined columns

---

## EPIC 11: QR Code Campaigns

### User Story 11.1: Generate Campaign QR Codes
**As an** administrator  
**I want to** generate QR codes for marketing campaigns  
**So that** I can track acquisition sources

**Acceptance Criteria:**
- [ ] Admin endpoint: `POST /api/v1/admin/campaigns/qr`
- [ ] Input: campaign name, destination (meeting_id or generic)
- [ ] Generates URL: `/meet?source=qr&campaign={campaign_id}&dest={meeting_id}`
- [ ] Returns QR code image (PNG, SVG)
- [ ] QR code stored in `qr_campaigns` table with ID
- [ ] Source tracked on session creation
- [ ] Downloadable from admin panel

**API Endpoint:** `POST /api/v1/admin/campaigns/qr`
```json
Request: {
  "campaign_name": "Downtown Flyer",
  "meeting_id": "uuid"
}
Response: {
  "campaign_id": "camp_abc123",
  "qr_url": "https://myverifiedcompliance.com/meet?source=qr&campaign=camp_abc123",
  "qr_image_url": "https://cdn.../qr_camp_abc123.png"
}
```

---

### User Story 11.2: Track Campaign Performance
**As an** administrator  
**I want to** see which QR campaigns drive sessions  
**So that** I can optimize marketing efforts

**Acceptance Criteria:**
- [ ] Admin dashboard section: "Campaign Performance"
- [ ] Table shows: campaign name, sessions started, sessions completed, completion rate
- [ ] Date range filter
- [ ] Sort by sessions (descending)
- [ ] Export to CSV

**API Endpoint:** `GET /api/v1/admin/campaigns/stats`
```json
Query Params: { from, to }
Response: {
  "campaigns": [
    {
      "campaign_id": "camp_abc123",
      "name": "Downtown Flyer",
      "sessions_started": 84,
      "sessions_completed": 71,
      "completion_rate": 84.5
    }
  ]
}
```

---

## EPIC 12: Testing & Quality Assurance

### User Story 12.1: Unit Tests for Backend
**As a** developer  
**I want** comprehensive unit tests  
**So that** core logic is validated

**Acceptance Criteria:**
- [ ] Test coverage >80% for API endpoints
- [ ] Tests for:
  - Contact upsert logic
  - Session state transitions
  - GPS distance calculations (Haversine)
  - Token generation and validation
  - HMAC signature verification
  - Geocoding fallback
- [ ] Pytest framework with fixtures
- [ ] Mocked external APIs (GHL, Google Maps)
- [ ] CI/CD integration (GitHub Actions)
- [ ] Test database separate from production

---

### User Story 12.2: Integration Tests for GHL
**As a** developer  
**I want** integration tests for GHL workflows  
**So that** CRM sync is reliable

**Acceptance Criteria:**
- [ ] Test GHL contact upsert (mock API)
- [ ] Test custom field updates
- [ ] Test tag additions/removals
- [ ] Test webhook payload signing and delivery
- [ ] Test retry logic on failures
- [ ] Validate webhook_logs entries
- [ ] Use GHL sandbox/test account for live testing

---

### User Story 12.3: Flutter Widget Tests
**As a** developer  
**I want** widget tests for key screens  
**So that** UI behavior is validated

**Acceptance Criteria:**
- [ ] Test coverage >70% for widgets
- [ ] Tests for:
  - Meeting Finder list rendering
  - Check-In/Check-Out button states
  - Search and filter logic
  - Log selection and export modals
  - Error state displays
- [ ] Golden tests for critical screens (snapshot comparison)
- [ ] Mocked API responses with mockito
- [ ] Run tests in CI/CD

---

### User Story 12.4: End-to-End Tests
**As a** QA engineer  
**I want** automated E2E tests  
**So that** critical user flows are validated

**Acceptance Criteria:**
- [ ] E2E framework: Flutter integration_test or Appium
- [ ] Test scenarios:
  - Complete session flow (onboarding → meeting selection → CI → CO → share)
  - Dashboard search and filter
  - Email export
  - Offline mode behavior
  - GPS permission denial and retry
- [ ] Run on real devices (iOS, Android) in CI/CD
- [ ] Video recording of test runs
- [ ] Slack notification on failures

---

## EPIC 13: Deployment & DevOps

### User Story 13.1: Backend Deployment Pipeline
**As a** DevOps engineer  
**I want** automated backend deployment  
**So that** releases are fast and reliable

**Acceptance Criteria:**
- [ ] Dockerized FastAPI app with multi-stage build
- [ ] Environment: Fly.io, Render, or AWS App Runner
- [ ] CI/CD: GitHub Actions workflow
  - Trigger on push to `main`
  - Run tests
  - Build Docker image
  - Push to container registry
  - Deploy to production
- [ ] Zero-downtime deployment (health checks)
- [ ] Rollback capability
- [ ] Environment variables managed via platform secrets
- [ ] HTTPS enforced, custom domain configured

---

### User Story 13.2: Database Migrations
**As a** developer  
**I want** version-controlled database migrations  
**So that** schema changes are tracked

**Acceptance Criteria:**
- [ ] Use Alembic for migrations (Python)
- [ ] Migrations stored in `/migrations` directory
- [ ] Commands: `alembic upgrade head`, `alembic downgrade -1`
- [ ] Auto-run on deployment (via entrypoint script)
- [ ] Backup database before migration (automated)
- [ ] Migration history visible in admin panel

---

### User Story 13.3: Flutter App Distribution
**As a** DevOps engineer  
**I want** automated app builds  
**So that** releases are published quickly

**Acceptance Criteria:**
- [ ] CI/CD: Codemagic or GitHub Actions
- [ ] Build triggers: tag push (`v1.0.0`)
- [ ] iOS: Build IPA, upload to TestFlight
- [ ] Android: Build APK/AAB, upload to Google Play Console (internal track)
- [ ] Version bumping automated (pubspec.yaml)
- [ ] Changelog generated from git commits
- [ ] Slack notification on successful build

---

### User Story 13.4: Monitoring & Logging
**As a** DevOps engineer  
**I want** centralized logging and monitoring  
**So that** issues are detected quickly

**Acceptance Criteria:**
- [ ] Backend logging: structured JSON logs (Python `logging`)
- [ ] Log aggregation: Sentry or Logtail
- [ ] Error tracking: Sentry for backend and Flutter
- [ ] Metrics: track API response times, error rates, session creation rate
- [ ] Alerts: Slack/PagerDuty for critical errors (5xx rate >5%, database down)
- [ ] Uptime monitoring: UptimeRobot or Pingdom (check `/health` endpoint)
- [ ] Dashboard: Grafana or platform-provided metrics

---

## EPIC 14: Documentation & Handoff

### User Story 14.1: API Documentation
**As a** developer  
**I want** comprehensive API documentation  
**So that** integration is straightforward

**Acceptance Criteria:**
- [ ] OpenAPI 3.0 spec generated from FastAPI
- [ ] Hosted at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- [ ] All endpoints documented with:
  - Description
  - Request/response schemas
  - Authentication requirements
  - Example payloads
  - Error codes
- [ ] Postman collection exported and included in repo
- [ ] README with quick start guide

---

### User Story 14.2: GHL Setup Guide
**As an** administrator  
**I want** step-by-step GHL configuration instructions  
**So that** I can set up the integration myself

**Acceptance Criteria:**
- [ ] Documentation includes:
  - How to create custom fields (with exact names)
  - How to create tags
  - How to set up Incoming Webhook workflow
  - How to configure HMAC secret
  - How to test webhook delivery
- [ ] Screenshots for each step
- [ ] Troubleshooting section (common errors)
- [ ] Exported GHL workflow JSON included in repo
- [ ] Video walkthrough (Loom or similar, <10 minutes)

---

### User Story 14.3: Developer Handoff Package
**As a** developer  
**I want** a complete handoff package  
**So that** I can deploy and maintain the app

**Acceptance Criteria:**
- [ ] Repository includes:
  - README with architecture overview
  - `.env.example` with all required variables
  - Makefile or scripts for common tasks (setup, migrate, test, deploy)
  - Postman collection for API testing
  - GHL workflow export JSON
  - Database schema diagram (ERD)
  - Deployment instructions (Fly.io, Render, etc.)
- [ ] Video walkthrough (Loom):
  - Code structure tour (15 minutes)
  - Local development setup (10 minutes)
  - Deployment walkthrough (10 minutes)
  - GHL integration demo (10 minutes)
- [ ] Runbook for common tasks:
  - Adding a new API endpoint
  - Creating a database migration
  - Debugging GHL webhook failures
  - Rotating HMAC secret

---

## EPIC 15: Performance & Optimization

### User Story 15.1: API Response Time Optimization
**As a** user  
**I want** fast API responses  
**So that** the app feels snappy

**Acceptance Criteria:**
- [ ] Target: 95th percentile <300ms for all endpoints
- [ ] Database indexing:
  - `contacts(email, phone, ghl_contact_id)`
  - `meetings(lat, lng)` for geospatial queries
  - `sessions(contact_id, created_at)`
  - `session_events(session_id, type)`
- [ ] Query optimization: use EXPLAIN ANALYZE to identify slow queries
- [ ] Connection pooling: configure pg pool size (min 5, max 20)
- [ ] Caching: Redis for meeting list (TTL 5 minutes)
- [ ] Load testing: simulate 100 concurrent users, verify no degradation

---

### User Story 15.2: Flutter App Performance
**As a** user  
**I want** smooth animations and fast screen loads  
**So that** the app feels premium

**Acceptance Criteria:**
- [ ] Target: 60 FPS on all screens
- [ ] Profile with Flutter DevTools, eliminate jank
- [ ] Optimize list rendering: use `ListView.builder` with `itemExtent`
- [ ] Image optimization: compress images, use cached_network_image
- [ ] Lazy loading: load next page of logs when scrolling near bottom
- [ ] App size: <50MB (release build)
- [ ] Startup time: <2 seconds on mid-range devices

---

### User Story 15.3: Database Backup & Recovery
**As an** administrator  
**I want** automated database backups  
**So that** data is protected

**Acceptance Criteria:**
- [ ] Daily automated backups (3 AM UTC)
- [ ] Retention: 7 daily, 4 weekly, 12 monthly
- [ ] Backup storage: AWS S3 or platform-provided
- [ ] Encryption at rest (AES-256)
- [ ] Test restore monthly (validation job)
- [ ] Recovery time objective: <1 hour
- [ ] Backup monitoring: alert if backup fails

---

## CROSS-CUTTING CONCERNS

### Accessibility
**Acceptance Criteria:**
- [ ] All interactive elements have semantic labels
- [ ] Minimum touch target size: 48dp
- [ ] Color contrast ratio ≥4.5:1 (WCAG AA)
- [ ] Screen reader support (TalkBack, VoiceOver)
- [ ] Keyboard navigation support (web views)
- [ ] Error messages announced to screen readers
- [ ] Forms have proper labels and hint text

### Internationalization (i18n)
**Acceptance Criteria:**
- [ ] All user-facing strings externalized (Flutter: ARB files)
- [ ] Support for English (en-US) as MVP
- [ ] Date/time formatted per device locale
- [ ] Distance units: miles (US) or kilometers (other)
- [ ] Future-ready: structure allows adding Spanish, etc.

### Security Checklist
- [ ] All API endpoints authenticated (except public share page)
- [ ] Input validation on all user inputs (sanitize, validate types)
- [ ] SQL injection protection (use parameterized queries)
- [ ] XSS protection (escape user-generated content)
- [ ] CSRF protection (not applicable for API-only backend)
- [ ] Rate limiting: 100 requests/minute per IP
- [ ] Secrets stored in environment variables, never in code
- [ ] Dependency scanning: Dependabot enabled
- [ ] Penetration testing before production launch

### Compliance & Legal
- [ ] Privacy Policy page (required before app store submission)
- [ ] Terms of Service page
- [ ] Consent checkbox required during onboarding
- [ ] Data deletion capability (future, GDPR compliance)
- [ ] Disclaimer on public share page: "Voluntary tracking, not court-admissible"
- [ ] Copyright notice in footer

---

## PRIORITY & SEQUENCING

### Phase 1: MVP (Weeks 1-4)
**Goal:** Core session flow working end-to-end
- Epic 1: User Onboarding (1.1, 1.2)
- Epic 2: Meeting Discovery (2.1, 2.3)
- Epic 3: Check-In/Check-Out (3.1, 3.3)
- Epic 6: GHL Integration (6.1, 6.2, 6.3, 6.4)
- Epic 13: Deployment (13.1, 13.2)

### Phase 2: Dashboard & Export (Weeks 5-6)
- Epic 4: Activity Logs (4.1, 4.6, 4.7, 4.8)
- Epic 3: Session Notes (3.2)
- Epic 5: Public Share Page (5.1, 5.2)

### Phase 3: Search, Filter & Polish (Weeks 7-8)
- Epic 4: Search & Filters (4.2, 4.3, 4.4, 4.5, 4.9)
- Epic 2: Meeting Search (2.2)
- Epic 8: Offline Support (8.1, 8.2, 8.3, 8.4)

### Phase 4: Admin & Analytics (Weeks 9-10)
- Epic 9: Admin Tools (9.1, 9.2, 9.3)
- Epic 10: Analytics (10.1, 10.2, 10.3)
- Epic 11: QR Campaigns (11.1, 11.2)

### Phase 5: Testing & Launch (Weeks 11-12)
- Epic 12: Testing (all stories)
- Epic 14: Documentation (all stories)
- Epic 15: Performance (all stories)
- App store submission preparation
- Production launch

---

## DEFINITION OF DONE (Per User Story)

A user story is considered "done" when:
- [ ] Code written and peer-reviewed
- [ ] Unit tests written and passing (>80% coverage for backend, >70% for Flutter)
- [ ] Integration tests passing (where applicable)
- [ ] Manual QA testing completed (test on iOS and Android)
- [ ] API endpoint documented in OpenAPI spec
- [ ] Deployed to staging environment
- [ ] Acceptance criteria validated by product owner
- [ ] No critical or high-priority bugs
- [ ] Responsive on mobile devices (tested on 3 screen sizes)
- [ ] Accessibility requirements met
- [ ] Merged to `main` branch

---

## TECH STACK SUMMARY

**Frontend (Flutter)**
- Flutter SDK 3.16+
- Dart 3.0+
- Key packages: `geolocator`, `http`, `provider` or `riverpod`, `sqflite`, `connectivity_plus`, `flutter_secure_storage`, `qr_flutter`, `cached_network_image`

**Backend (Python)**
- FastAPI 0.104+
- Python 3.11+
- PostgreSQL 15+ (with PostGIS for geospatial queries)
- Key packages: `sqlalchemy`, `alembic`, `pydantic`, `httpx`, `python-jose` (JWT), `passlib`, `pytest`

**Infrastructure**
- Hosting: Fly.io / Render / AWS App Runner
- Database: Managed PostgreSQL (Neon, Supabase, or AWS RDS)
- File storage: AWS S3 (for QR codes, exports)
- Monitoring: Sentry, Logtail
- CI/CD: GitHub Actions

**Third-Party Integrations**
- GoHighLevel (CRM via API)
- Google Maps API (geocoding, static maps)
- Email: SMTP or SendGrid (for log exports)

---

## RISK REGISTER

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| GHL API rate limits | High | Medium | Implement exponential backoff, queue webhooks |
| GPS accuracy issues in urban areas | Medium | High | Set 200m threshold, flag questionable locations |
| Users disable GPS permissions | High | Medium | Clear onboarding, show value proposition |
| Token expiration during active session | Medium | Low | 15-minute TTL reasonable, add refresh mechanism if needed |
| Database performance at scale | High | Low | Indexing, caching, regular monitoring |
| App store rejection | High | Low | Follow guidelines, privacy policy, content review |
| HMAC secret compromise | Critical | Low | Rotate secrets regularly, monitor webhook logs |

---

**END OF DOCUMENT**

Total Epics: 15  
Total User Stories: 60+  
Estimated Timeline: 12 weeks (3 developers)