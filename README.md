<div align="center">

# ParkEase

**Smart parking management platform — find, reserve, pay for and manage parking in real time.**

A production-style, full-stack web application built with Flask and vanilla JavaScript. ParkEase models a 10-city parking network with live slot availability, multi-slot bookings, wallet/UPI payments with admin-verified screenshots, QR check-in, digital receipts and role-based dashboards.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-5-010101?logo=socket.io&logoColor=white)](https://flask-socketio.readthedocs.io/)
[![Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=white)](https://render.com/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Getting Started](#getting-started)
- [Demo Credentials](#demo-credentials)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Real-Time Events](#real-time-events)
- [Business Rules](#business-rules)
- [Testing](#testing)
- [Deploying to Render](#deploying-to-render)
- [Production Considerations](#production-considerations)
- [Security Notes](#security-notes)
- [License](#license)

---

## Overview

ParkEase is a single-deploy parking platform. The Flask backend serves both a JSON API under `/api/**` and the static single-page frontend from `frontend/`, so the whole product runs as one service with no separate build step for the UI.

Users can search a real network of facilities across ten Indian cities, check live slot availability by vehicle type (Car / Bike / Truck / EV), reserve up to four slots at once, pay by wallet or verified UPI, check in with a QR code and download a PDF receipt. Administrators get a control panel with a payment-verification queue, user management, facility management, revenue analytics and CSV exports.

State changes are pushed to connected browsers over Socket.IO, so bookings, payments and notifications update live without polling the API.

---

## Features

### For drivers
- **City & proximity search** — filter facilities by city, vehicle type and free-text query; radius search using the Haversine formula.
- **Live slot availability** — per-facility counts for Car, Bike, Truck and EV, refreshed in real time.
- **Multi-slot bookings** — reserve up to 4 slots in one booking, each with its own vehicle number (strict 1:1 slot-to-vehicle validation).
- **Transparent pricing** — automatic weekend, weekly, monthly and early-bird discounts, 18% GST, and a live price breakdown before confirmation.
- **QR check-in / check-out** — scannable QR is generated per booking; slots are held on reservation and released on completion, cancellation or expiry.
- **Payments** — wallet with instant refunds and balance, or UPI via a generated QR + screenshot upload that an admin verifies.
- **Digital receipts** — downloadable GST PDF receipts (ReportLab).
- **Notifications** — in-app notification centre with unread badge, delivered instantly over WebSocket.

### For administrators
- **Dashboard metrics** — users, facilities, bookings, active bookings, pending verifications, today's and month-to-date revenue, and occupancy by vehicle type.
- **Payment verification queue** — review UPI screenshots (served through an auth-gated route), approve to confirm a booking, or reject to cancel and refund the held slots.
- **Booking & user management** — filter/paginate bookings, search users, block/unblock accounts.
- **Facility management** — create facilities (auto-generating their slot inventory) and update pricing.
- **Revenue analytics** — daily revenue, revenue by vehicle type and top facilities.
- **CSV reports** — export bookings and revenue for a date range.

### Admin Panel UI
The admin dashboard is a single-page interface accessible at `/admin` (requires admin role). It features:
- **Verifications tab** — real-time payment screenshot queue with image preview, transaction details, and approve/reject actions with mandatory rejection notes.
- **Bookings tab** — paginated, filterable table of all bookings with quick access to verification and receipt download.
- **Users tab** — searchable user list with role badges, wallet balance, block/unblock toggle.
- **Facilities tab** — list of all facilities (including inactive) with slot counts, ratings, and a modal to create new facilities with auto-generated slot inventory.
- **Revenue tab** — 30-day revenue breakdown by vehicle type, daily booking trends, and top-performing facilities.
- **Live updates** — the verifications queue auto-refreshes every 20s and receives instant Socket.IO notifications when new screenshots are submitted.

### Platform
- JWT authentication (access + refresh) via headers **and** cookies, with refresh-token rotation.
- Rate limiting (Flask-Limiter), CORS, request validation, hashed passwords (Werkzeug).
- Lazy booking lifecycle sweep — active bookings that pass their end time are auto-completed and their slots released.
- Zero frontend framework/build tooling; responsive, accessible, multi-file CSS.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.11 |
| Web framework | Flask 3.0 |
| ORM / database | Flask-SQLAlchemy 3.1 · SQLite (dev) · PostgreSQL (production) |
| Auth | Flask-JWT-Extended 4.6 (access + refresh tokens, header & cookie storage) |
| Real-time | Flask-SocketIO 5.3 + python-socketio (threading mode) |
| Validation / security | Flask-CORS, Flask-Limiter, Werkzeug password hashing |
| Documents | ReportLab (PDF receipts), qrcode (booking & UPI QR codes) |
| Frontend | Vanilla JavaScript (SPA), HTML5, hand-written CSS, Socket.IO client (CDN) |
| Server | Gunicorn (gthread worker) |
| Testing | pytest + pytest-cov |
| Deployment | Render (Blueprint / `render.yaml`) |

---

## Architecture

```
                        ┌──────────────────────────────────────────┐
                        │                Browser (SPA)             │
                        │  index.html · js/api.js · js/main.js     │
                        │  Socket.IO client ←→ fetch/Bearer JWT    │
                        └───────────────┬──────────────┬───────────┘
                             HTTPS/REST │              │ WebSocket / long-poll
                                        ▼              ▼
                        ┌──────────────────────────────────────────┐
                        │            Flask app (run.py)            │
                        │  /api/**  blueprint routes               │
                        │  /        static frontend                │
                        │  /screenshots/**  auth-gated uploads     │
                        ├──────────────────────────────────────────┤
                        │  Middleware · Utils · Socket.IO server   │
                        │  auth · pricing · lifecycle · notifier   │
                        └───────────────┬──────────────────────────┘
                                        │ SQLAlchemy
                                        ▼
                        ┌──────────────────────────────────────────┐
                        │      SQLite (dev) / PostgreSQL (prod)    │
                        └──────────────────────────────────────────┘
```

The app is created by `create_app(with_socketio=True)` in `backend/app.py`. On import it initialises the database (`db.create_all()`), registers all blueprints, mounts the static frontend and the Socket.IO server, and exposes an authenticated handshake that places each connection into `user_<id>`, `admins` and `booking_<id>` rooms.

---

## Project Structure

```
smartParking/
├── run.py                     # Entry point: create_app + socketio.run / WSGI target (run:app)
├── requirements.txt           # Root file Render installs (re-exports backend/requirements.txt)
├── render.yaml                # Render Blueprint (web service + PostgreSQL)
├── .python-version            # Pinned Python for Render
├── .env.example               # Documented environment variables
│
├── backend/
│   ├── app.py                 # Application factory, static serving, Socket.IO, error handlers
│   ├── config.py              # Config classes (dev / prod / testing) + env overrides
│   ├── models.py              # SQLAlchemy models
│   ├── seed_data.py           # Seeds admin, demo user and 20 facilities
│   ├── requirements.txt       # Pinned dependencies
│   ├── middleware/
│   │   └── auth_middleware.py # admin_required, get_current_user_id, optional_jwt
│   ├── routes/
│   │   ├── auth_routes.py         # /api/auth
│   │   ├── user_routes.py         # /api/users
│   │   ├── facility_routes.py     # /api/facilities
│   │   ├── booking_routes.py      # /api/bookings
│   │   ├── payment_routes.py      # /api/payments
│   │   ├── notification_routes.py # /api/notifications
│   │   └── admin_routes.py        # /api/admin
│   └── utils/
│       ├── helpers.py             # utcnow, pricing, slot locking, serialisation
│       ├── lifecycle.py           # Auto-complete expired bookings
│       ├── notifier.py            # Notification creation + Socket.IO emit
│       ├── qr_generator.py        # Booking / UPI QR generation
│       ├── receipt_generator.py   # PDF receipts
│       └── validators.py          # Registration / login / vehicle validation
│
└── frontend/
    ├── index.html             # Single-page app shell and all views
    ├── css/                   # style, app, notifications, responsive, animations
    └── js/
        ├── api.js             # Fetch wrapper, token refresh, protected image fetch
        └── main.js            # Router, views, bookings, payments, admin, sockets
```

---

## Data Model

| Model | Purpose |
| --- | --- |
| `User` | Account with `role` (`user`/`admin`), wallet balance, block/verify flags, hashed password. |
| `Vehicle` | A user's saved vehicle numbers and types (`unique` per user). |
| `Facility` | A parking site with location, per-type totals/availability, hourly & monthly rates, amenities, hours, rating. |
| `Slot` | An individual parking space (`slot_code`, `vehicle_type`, occupancy + `occupied_until`). |
| `Booking` | A reservation across one or more slots with pricing, payment status, status, QR and check-in/out timestamps. |
| `BookingVehicle` | One vehicle number per booked slot (a booking can cover several slots). |
| `Payment` | A payment attempt/record linked to a booking (wallet, UPI, verification metadata). |
| `Notification` | Per-user in-app notification with type, title, message and deep link. |

Booking status flow: `reserved → confirmed → active → completed`, with `cancelled` as a terminal branch.

---

## Getting Started

### Prerequisites
- Python **3.11** (3.10+ should work; 3.12 is untested with `eventlet`)
- pip
- Git

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url> smartParking
cd smartParking

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the environment

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

The defaults work out of the box for local development (SQLite database, insecure dev secrets). See [Configuration](#configuration) for the full variable list.

### 4. Seed the database

Creates an admin, a demo user and 20 facilities across 10 cities (with all slots):

```bash
python -m backend.seed_data          # skips if an admin already exists
python -m backend.seed_data --reset  # drop everything and reseed
```

### 5. Run the server

```bash
python run.py
```

Then open **http://localhost:5000**. The API health check is at `GET /api/health`.

> For a production-style run locally:
> ```bash
> gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 100 run:app
> ```

---

## Demo Credentials

Seeded by `backend/seed_data.py`:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@parkease.com` | `Admin@123` |
| User | `demo@parkease.com` | `Demo@123` |

> Change or remove these before exposing a public deployment.

---

## Configuration

All settings are environment variables (see `.env.example`). Sensible defaults let the app run locally with no configuration.

| Variable | Default | Description |
| --- | --- | --- |
| `FLASK_ENV` | `development` | Config selector: `development`, `production`, `testing`. |
| `SECRET_KEY` | insecure dev value | Flask session/signing key. **Set in production.** |
| `JWT_SECRET_KEY` | insecure dev value | JWT signing key. **Set in production.** |
| `DATABASE_URL` | `sqlite:///parkease.db` | SQLAlchemy connection string. `postgres://` is auto-normalised to `postgresql://`. |
| `CORS_ORIGINS` | localhost + Render URL | Comma-separated allowed origins. Locally defaults to localhost; on Render `RENDER_EXTERNAL_URL` is added automatically. |
| `LOCAL_TIMEZONE` | `Asia/Kolkata` | Timezone used for discount business rules. |
| `MERCHANT_UPI` | `6305898891@upi` | Merchant VPA embedded in the generated UPI QR. |
| `MERCHANT_NAME` | `ParkEase` | Merchant name in the UPI QR. |
| `DATA_DIR` | `backend/` | Base directory for runtime files (uploads/receipts/QR/screenshots). Point at a persistent volume. |
| `UPLOAD_FOLDER` / `RECEIPT_FOLDER` / `QR_CODE_FOLDER` / `SCREENSHOT_FOLDER` | under `DATA_DIR` | Individual overrides for storage locations. |
| `RATELIMIT_DEFAULT` | `200 per minute` | Default rate limit. |
| `RATELIMIT_STORAGE_URL` | `memory://` | Rate-limit backend; use Redis for multi-instance. |

---

## API Reference

- **Base URL:** `/api`
- **Auth:** send `Authorization: Bearer <access_token>` (cookies are also supported). Endpoints marked **Admin** require an admin JWT.
- **Content type:** `application/json` (except CSV/PDF downloads and screenshot uploads which carry base64 image data).

### Auth — `/api/auth`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/register` | — | Create an account; returns user + tokens. |
| POST | `/login` | — | Authenticate; returns user + tokens. |
| POST | `/logout` | ✔ | Clear auth cookies. |
| POST | `/refresh` | refresh token | Issue a new access token. |
| GET | `/verify` | ✔ | Validate the current token, return the user. |
| PUT | `/change-password` | ✔ | Change password (validates complexity). |

### Users — `/api/users`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/profile` | ✔ | Get the current user's profile. |
| PUT | `/profile` | ✔ | Update name / phone. |
| GET | `/vehicles` | ✔ | List saved vehicles. |
| POST | `/vehicles` | ✔ | Add a vehicle. |
| DELETE | `/vehicles/{id}` | ✔ | Remove a vehicle. |
| PUT | `/vehicles/{id}/default` | ✔ | Set the default vehicle. |
| GET | `/bookings` | ✔ | Paginated bookings for the user (`status`, `page`, `per_page`). Auto-completes expired bookings. |

### Facilities — `/api/facilities`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `` | — | List/filter facilities (`city`, `vehicle_type`, `latitude`, `longitude`, `radius`, `page`, `per_page`). |
| GET | `/{id}` | — | Facility detail (optionally with slots). |
| GET | `/search` | — | Text search across name/area/city/street (`q`). |
| GET | `/{id}/slots` | — | Available slots (`vehicle_type`, `start_time`, `end_time`). |
| GET | `/cities` | — | Distinct active cities. |
| POST | `` | **Admin** | Create a facility + its slot inventory. |
| PUT | `/{id}` | **Admin** | Update facility details/pricing. |
| DELETE | `/{id}` | **Admin** | Deactivate a facility (soft delete). |

### Bookings — `/api/bookings`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `` | ✔ | Create a booking (1–4 slots, one vehicle per slot). |
| POST | `/price-estimate` | — | Preview pricing without booking. |
| GET | `/{id}` | ✔ | Booking detail (owner or admin). |
| PUT | `/{id}` | ✔ | Modify times/slots/vehicles (before start). |
| DELETE | `/{id}` | ✔ | Cancel (refunds per policy). |
| POST | `/{id}/checkin` | ✔ | Check in (requires paid; opens 30 min early). |
| POST | `/{id}/checkout` | ✔ | Check out early; releases slots. |
| GET | `/{id}/receipt` | ✔ | Download the PDF receipt (owner or admin). |

### Payments — `/api/payments`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/initiate` | ✔ | Start wallet (immediate) or UPI payment. |
| POST | `/upi/qr` | ✔ | Generate the UPI QR + pricing breakdown. |
| POST | `/upi/upload-screenshot` | ✔ | Upload a payment screenshot for admin verification. |
| POST | `/admin/verify-screenshot/{payment_id}` | **Admin** | Approve/reject a screenshot. |
| POST | `/verify` | ✔ | Verify a simulated gateway payment. |
| POST | `/refund` | **Admin** | Refund to a user's wallet. |
| GET | `/history` | ✔ | Payment history for the user. |
| GET | `/wallet` | ✔ | Wallet balance. |
| POST | `/wallet/add` | ✔ | Add funds (1–50000). |
| GET | `/status/{booking_id}` | ✔ | Current payment status (owner or admin). |
| POST | `/webhook` | — | Gateway webhook for async payment updates. |

### Notifications — `/api/notifications`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `` | ✔ | List notifications (`limit`, `unread_only`). |
| GET | `/unread-count` | ✔ | Unread badge count. |
| PUT | `/{id}/read` | ✔ | Mark one as read. |
| PUT | `/read-all` | ✔ | Mark all read (and prune history). |
| DELETE | `/{id}` | ✔ | Delete one. |
| DELETE | `/read-all` | ✔ | Clear all. |

### Admin — `/api/admin`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/dashboard` | **Admin** | KPIs + occupancy. Also sweeps expired bookings. |
| GET | `/payments/pending` | **Admin** | Payment verification queue. |
| GET | `/revenue` | **Admin** | Revenue analytics (`days`). |
| GET | `/bookings` | **Admin** | All bookings (`status`, `facility_id`, `user_id`, `page`). |
| GET | `/users` | **Admin** | All users (`search`, `role`, `is_blocked`, `page`). |
| PUT | `/users/{id}/block` | **Admin** | Toggle block/unblock. |
| PUT | `/pricing` | **Admin** | Update a facility's rates. |
| GET | `/facilities` | **Admin** | All facilities (incl. inactive). |
| GET | `/reports/bookings` | **Admin** | CSV export (date range). |
| GET | `/reports/revenue` | **Admin** | CSV revenue export (date range). |

### System

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/health` | — | Service health (`{"status": "healthy"}`). |
| GET | `/screenshots/{filename}` | ✔ | Payment screenshot (admin or owning user). |
| GET | `/` · `/{path}` | — | Static frontend assets. |

---

## Real-Time Events

The client connects with its access token: `io({ auth: { token } })`. The server authenticates the handshake and joins the connection to `user_<id>`, `admins` (for admins) and any `booking_<id>` room on request.

**Client → server**

| Event | Payload | Purpose |
| --- | --- | --- |
| `join_booking` | `{ booking_id }` | Subscribe to a booking's updates. |
| `leave_booking` | `{ booking_id }` | Unsubscribe. |

**Server → client**

| Event | Room | Purpose |
| --- | --- | --- |
| `notification` | `user_<id>` | A new in-app notification. |
| `notification_admin` | `admins` | Admin-targeted notification (e.g. new verification). |
| `payment_initiated` | `booking_<id>` | Payment started. |
| `payment_paid` | `booking_<id>` | Payment succeeded. |
| `payment_failed` | `booking_<id>` | Payment failed. |
| `payment_screenshot_uploaded` | `booking_<id>` | A UPI screenshot was submitted. |
| `booking_updated` | `booking_<id>` / `user_<id>` | Booking status changed (confirm/cancel/expire/verify). |

---

## Business Rules

### Pricing
- **Hourly / daily:** rate × duration. **Monthly:** monthly rate × months.
- **Multi-slot:** the base price scales with the number of slots booked.
- **Discounts** (evaluated in `LOCAL_TIMEZONE`): weekend 15%, weekly (≥7 days) 10%, monthly 20%, early bird (before 09:00) 5% — capped at 50% of the base price.
- **GST:** 18% applied after discounts.

### Booking lifecycle
- Slots are held (`occupied_until = end_time`) at reservation and released on expiry, cancellation or rejection.
- Check-in requires a paid booking and is allowed from 30 minutes before the start time.
- Active bookings whose end time passes are **auto-completed** by a lazy sweep triggered on booking/admin reads (`backend/utils/lifecycle.py`), which frees the slots and notifies the user.

### Cancellation refunds
Applies when the booking was paid:
- ≥ 24 hours before start → **100%**
- 2–24 hours before start → **50%**
- < 2 hours before start → **0%**

Refunds are credited to the in-app wallet.

---

## Testing

The backend ships with pytest configured:

```bash
pip install -r requirements.txt
pytest
# with coverage
pytest --cov=backend
```

`TestingConfig` uses an in-memory SQLite database and writes uploads to a temporary folder, so test runs never touch your real data or leave files behind.

> Set `FLASK_ENV=testing` when building an app context in tests.

### Test Suite Coverage
- **Price calculation** — hourly, multi-slot, weekly, weekend, early-bird, and monthly discounts with GST.
- **Slot locking** — successful locks, conflict detection, and release.
- **Booking validation** — 1:1 vehicle-per-slot rule, duplicate detection, missing numbers.
- **Input validators** — registration, login, and vehicle data validation.
- **DateTime helpers** — ISO parsing with/without offsets, UTC formatting.
- **Facility availability sync** — denormalized counts stay in sync with Slot table.
- **Auth flow** — register, login, token verify, logout.
- **Booking flow** — create booking, price estimate endpoints.

### Test Client Notes
When using Flask's test client with JWT cookies, subsequent requests automatically include the `access_token_cookie`. For `Authorization: Bearer` header testing, use `test_request_context` or `environ_overrides={'HTTP_AUTHORIZATION': 'Bearer <token>'}` as the test client may not propagate the header on POST requests in-process.

---

## Deploying to Render

ParkEase ships with a ready-to-use [Render Blueprint](https://render.com/docs/blueprint-spec) (`render.yaml`) that provisions a **web service** and a **PostgreSQL database**, wiring the connection string in automatically.

### Option A — One-click Blueprint (recommended)

1. Push this repository to GitHub/GitLab.
2. In the Render Dashboard: **New → Blueprint**.
3. Select the repo. Render reads `render.yaml` and shows the resources it will create.
4. Click **Apply**. Render will:
   - build with `pip install -r requirements.txt`,
   - start with `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 100 run:app`,
   - create PostgreSQL and inject `DATABASE_URL`,
   - generate `SECRET_KEY` and `JWT_SECRET_KEY`,
   - (optionally) prompt for `MERCHANT_UPI` — provide your VPA or skip it,
   - wait for `/api/health` to pass before routing traffic.
5. Once live, seed the database from the service **Shell** tab:
   ```bash
   python -m backend.seed_data
   ```
   Tables themselves are created automatically on first boot (`db.create_all()`).

### Option B — Manual web service

| Setting | Value |
| --- | --- |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 100 run:app` |
| Health Check Path | `/api/health` |

Then add a **PostgreSQL** instance and set the environment variables from the table in [Configuration](#configuration) — at minimum `FLASK_ENV=production`, `SECRET_KEY`, `JWT_SECRET_KEY`, and `DATABASE_URL` (copy the database's **Internal Connection String**).

### Why a single worker?
Flask-SocketIO runs in `threading` mode (`backend/app.py`) and keeps connection/room state in process memory. Concurrency comes from **threads within one worker**, not multiple worker processes — this is the [documented Gunicorn setup](https://flask-socketio.readthedocs.io/en/latest/deployment.html) for threaded mode. `simple-websocket` is installed so WebSocket transport works under the gthread worker (clients fall back to long-polling otherwise).

### Free-plan notes
- Free web services **spin down after ~15 minutes** of inactivity; the next request takes ~30–60 s to wake.
- Render's **free PostgreSQL expires after 30 days**. For anything beyond a demo, use a paid Postgres plan or an external database.
- The filesystem is **ephemeral**: uploaded screenshots, generated receipts and QR images are lost on redeploy. Add a **[Render Disk](https://render.com/docs/disks)** and point `DATA_DIR` (or the individual `*_FOLDER` variables) at the mount path to persist them. This requires a paid instance type.

### Environment variables quick reference (Render)

```
FLASK_ENV=production
SECRET_KEY=<generated>
JWT_SECRET_KEY=<generated>
DATABASE_URL=<from Render PostgreSQL>
MERCHANT_UPI=<your UPI VPA>      # optional
DATA_DIR=/var/data               # only if a persistent disk is attached
```

---

## Production Considerations

- **Migrations:** the app uses `db.create_all()` on startup. For evolving schemas, introduce [Flask-Migrate](https://flask-migrate.readthedocs.io/) / Alembic before making breaking model changes.
- **Scaling:** Socket.IO room state is in-memory, so horizontal scaling needs a message queue (e.g. Redis) as the Socket.IO `message_queue`, plus sticky sessions.
- **Rate limiting:** `memory://` is per-process; use a shared backend (Redis) if you run more than one instance.
- **Persistent storage:** attach a Render Disk (or migrate uploads to object storage such as S3/R2) for screenshots and receipts.
- **Secrets:** always set strong, unique `SECRET_KEY` / `JWT_SECRET_KEY`. Never commit `.env`.

---

## Security Notes

- Passwords are hashed with Werkzeug (PBKDF2).
- JWTs support access (24 h) and refresh (30 d) tokens with rotation; tokens can travel via header or HttpOnly cookie. In `production`, secure cookies are enforced.
- Uploaded payment screenshots are validated by magic bytes (PNG/JPEG/GIF/WEBP) and size-capped at 5 MB, and are served only to admins or the owning user via an auth-gated route.
- All admin routes are protected by `@jwt_required()` + `admin_required`.
- Input is validated for registration, login and vehicle data.

---

## License

This project is provided for educational and portfolio purposes. Add a `LICENSE` file (e.g. MIT) before distributing.

<div align="center"><sub>Built with Flask, SQLAlchemy and a lot of vanilla JavaScript.</sub></div>
