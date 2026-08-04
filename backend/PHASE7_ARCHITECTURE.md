# Phase 7 — Real-Time Communication Platform Architecture

> **Version:** Phase 7.8 (Production Audit)
> **Stack:** FastAPI + Socket.IO + Flutter + Firebase FCM + MongoDB + Cloudinary

---

## Module Overview

| Module | Phase | Backend | Flutter | Status |
|--------|-------|---------|---------|--------|
| Real-Time Infrastructure | 7.1 | `app/sockets/` | `socket_service.dart` | ✅ |
| Push Notification System | 7.2 | `app/notifications/` | `push_notification_service.dart` | ✅ |
| Booking Session Communication | 7.3 | `app/sockets/events.py` | `booking_chat_service.dart` | ✅ |
| Live Booking Tracking | 7.4 | `app/sockets/events.py` | `socket_service.dart` | ✅ |
| Live Worker Location | 7.5 | `app/sockets/events.py` | `location_service.dart` | ✅ |
| Booking Media Sharing | 7.6 | `app/uploads/` | `booking_chat_service.dart` | ✅ |
| Notification Center | 7.7 | `app/notifications/` | `notification_center_screen.dart` | ✅ |

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      Flutter App                             │
│                                                              │
│  Customer App              Worker App                        │
│  ──────────────            ────────────                      │
│  HomeScreen                WorkerDashboardScreen             │
│  BookingDetailsScreen      WorkerJobDetailsScreen            │
│  NotificationCenterScreen  (shares notification center)      │
│  BookingChatScreen         BookingChatScreen                 │
│  LiveTrackingSection       WorkerLocationTracker             │
│                                                              │
│  Services Layer                                              │
│  ─────────────                                               │
│  ApiService          ← REST calls (JWT Bearer)               │
│  SocketService       ← Socket.IO WebSocket                   │
│  BookingChatService  ← Chat + Media (Socket + REST)          │
│  LocationService     ← GPS + Nominatim reverse geocoding     │
│  NotificationService ← Notification history CRUD             │
│  PushNotificationService ← FCM token + deep linking          │
│                                                              │
│  State                                                       │
│  ─────                                                       │
│  TokenStorage (SharedPreferences)                            │
│  ├── accessToken, refreshToken, userId, userRole             │
└──────────────────────────────────────────────────────────────┘
            │ REST /api/v1         │ Socket.IO /socket.io
            ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│                                                              │
│  REST Routers                                                │
│  ─────────────                                               │
│  /notifications   — history, preferences, device mgmt        │
│  /uploads         — Cloudinary media upload (booking-gated)  │
│  /sockets         — health check                             │
│  (all other Phase 1-6 routes)                                │
│                                                              │
│  Socket.IO Layer                                             │
│  ────────────────                                            │
│  events.py        — all real-time event handlers             │
│  middleware.py    — JWT socket authentication                 │
│  connection_manager.py — sid↔user_id mapping                 │
│  presence_manager.py   — online/offline tracking             │
│  room_manager.py       — room naming conventions             │
│  rate_limiter.py       — in-memory rate limiting             │
│                                                              │
│  Notification Layer                                          │
│  ──────────────────                                          │
│  fcm_client.py    — Firebase Admin SDK wrapper               │
│  service.py       — orchestration (preferences, queue, retry)│
│  repository.py    — MongoDB CRUD for notifications           │
│  templates.py     — notification type → title/body           │
│                                                              │
│  Storage                                                     │
│  ────────                                                     │
│  MongoDB Atlas    — permanent + TTL collections              │
│  Cloudinary CDN   — booking media (images, PDFs)             │
│  In-memory        — presence, socket sessions, rate limits   │
└──────────────────────────────────────────────────────────────┘
```

---

## Socket.IO Event Reference

### Connection Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client→Server | Authenticated connection (JWT in auth dict) |
| `disconnect` | Server←Client | Cleanup: presence, auth cache, connection |
| `ping` | Client→Server | Latency check / keep-alive |

### Booking Chat Events (Phase 7.3)

| Event | Direction | Description |
|-------|-----------|-------------|
| `join_booking` | Client→Server | Join chat room (authorization verified) |
| `leave_booking` | Client→Server | Leave chat room |
| `send_message` | Client→Server | Send text/media message (authorization verified) |
| `receive_message` | Server→Client | Broadcast message to room |
| `typing_indicator` | Client→Server | Typing status |
| `typing_update` | Server→Client | Broadcast typing status |
| `read_receipt` | Client→Server | Mark message as read |
| `message_read` | Server→Client | Broadcast read receipt |

### Live Tracking Events (Phase 7.4 / 7.5)

| Event | Direction | Description |
|-------|-----------|-------------|
| `join_booking_tracking` | Client→Server | Join tracking room (authorization verified) |
| `leave_booking_tracking` | Client→Server | Leave tracking room |
| `update_booking_status` | Client→Server | Worker updates booking status (authorization verified) |
| `booking_status_updated` | Server→Client | Broadcast status update to tracking room |
| `update_worker_location` | Client→Server | Worker shares GPS coordinates (authorization verified) |
| `worker_location_updated` | Server→Client | Broadcast location to tracking room |

### Authorization Model

All booking-scoped events verify that the emitting `sid` belongs to the booking's `customer_id` or `worker_id`. Authorization is cached in memory on first `join_*` call to avoid DB round-trips per message. Cache is cleared on `disconnect`.

---

## FCM Notification Payload Structure

```json
{
  "notification": {
    "title": "Worker Assigned",
    "body": "John has been assigned to your booking."
  },
  "data": {
    "booking_id": "6881f7c2...",
    "type": "Booking Assigned"
  }
}
```

**Deep Link Routing:**
- `data.booking_id` present → navigate to booking details
- `TokenStorage.userRole == 'worker'` → `/worker/jobs/details`
- `TokenStorage.userRole == 'customer'` → `/customer/booking/details`

---

## Notification Types (templates.py)

| Type | Category | Can Disable |
|------|----------|-------------|
| `Booking Created` | Booking | ✅ |
| `Booking Accepted` | Booking | ✅ |
| `Booking Assigned` | Booking | ✅ |
| `Booking Cancelled` | Booking | ✅ |
| `Booking Completed` | Booking | ✅ |
| `Quotation Received` | Booking | ✅ |
| `Quotation Accepted` | Booking | ✅ |
| `Quotation Rejected` | Booking | ✅ |
| `Worker Arriving` | Booking | ✅ |
| `Worker Reached` | Booking | ✅ |
| `AI Recommendation Ready` | AI | ✅ |
| `Admin Broadcast` | System | ❌ (always delivered) |
| `System Announcement` | System | ❌ (always delivered) |

---

## MongoDB Collections

### Permanent Collections

| Collection | TTL | Notes |
|-----------|-----|-------|
| `users` | None | Core user accounts |
| `worker_profiles` | None | Worker credentials, ratings |
| `customer_profiles` | None | Customer profiles |
| `bookings` | None | Full booking lifecycle |
| `quotations` | None | Pricing quotes |
| `reviews` | None | Ratings & reviews |
| `refresh_tokens` | Via JWT expiry | Rotated on refresh |
| `device_tokens` | None (deactivated) | FCM tokens, deactivated on FCM rejection |

### TTL Collections (Auto-purged)

| Collection | TTL | Notes |
|-----------|-----|-------|
| `notifications` | 30 days | Metadata only — no payloads |
| `otp` | 5 min (from `expires_at`) | OTP codes |
| `auth_audit_logs` | 90 days | Login/logout audit trail |

### NOT Stored in MongoDB (by design)

- GPS coordinates / location updates → in-memory via Socket.IO only
- Socket sessions → Socket.IO server memory
- Notification payloads → FCM handles delivery; only metadata stored
- Chat message content → in-memory per session (ephemeral by design)

---

## Environment Variable Checklist

### Required in all environments

| Variable | Description |
|----------|-------------|
| `JWT_SECRET_KEY` | Minimum 32 characters |
| `MONGODB_URI` | MongoDB Atlas connection string |

### Required in production (enforced at startup)

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | Must not be localhost |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `FIREBASE_CREDENTIALS_PATH` | Path to serviceAccountKey.json |
| `ALLOWED_ORIGINS` | Must not contain `"*"` |

### Optional / Recommended

| Variable | Description | Default |
|----------|-------------|---------|
| `SOCKET_MESSAGE_QUEUE` | Redis URL for horizontal scaling | None (single-process) |
| `LOG_JSON_FORMAT` | Enable JSON logs for log aggregation | False |
| `LOG_LEVEL` | Log level | DEBUG |
| `ENVIRONMENT` | `development` / `staging` / `production` | development |

---

## API Endpoint Index

### Notifications (`/api/v1/notifications`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register-device` | User | Register FCM token |
| PUT | `/update-device` | User | Rotate FCM token |
| DELETE | `/remove-device` | User | Remove FCM token on logout |
| GET | `` | User | Get notification history (paginated) |
| GET | `/unread-count` | User | Get unread badge count |
| PUT | `/read/{id}` | User | Mark notification as read |
| PUT | `/read-all` | User | Mark all as read |
| DELETE | `/{id}` | User | Delete notification |
| DELETE | `/read-all` | User | Delete all read notifications |
| GET | `/preferences` | User | Get notification preferences |
| PUT | `/preferences` | User | Update notification preferences |
| POST | `/send` | Admin | Send to specific user |
| POST | `/broadcast` | Admin | Broadcast to all / by role |

### Uploads (`/api/v1/uploads`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/booking-media` | User | Upload image/PDF for active booking |

---

*Generated: Phase 7.8 Production Audit*
