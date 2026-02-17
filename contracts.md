# API Contracts (Portfolio)

This MVP currently uses **MOCKED** data for profile/projects. We are now replacing the **MOCKED contact form persistence** (localStorage) with MongoDB-backed APIs.

## Data currently mocked in frontend
- `src/mock.js`
  - `profile` (name, tagline, email, socials)
  - `skills`
  - `projects`
  - `about`

Only the **contact form persistence** will be migrated to backend in this step.

---

## Contact Submissions

### Model: ContactSubmission
Stored in MongoDB collection: `contact_submissions`

Fields:
- `id: string` (uuid)
- `name: string`
- `email: string`
- `message: string`
- `created_at: datetime` (UTC)

---

## Endpoints (all routes prefixed with `/api`)

### 1) Create contact submission (public)
**POST** `/api/contact`

Request body:
```json
{
  "name": "string",
  "email": "string",
  "message": "string"
}
```

Response (201):
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "message": "string",
  "created_at": "2026-02-17T18:26:00.000Z"
}
```

Errors:
- `422` validation errors (FastAPI/Pydantic)

Frontend integration:
- Replace localStorage write with `POST /api/contact`
- Show toast on success/failure
- Update “Recent submissions” UI from the in-memory list built from successful responses (no localStorage)

---

### 2) Recent submissions (admin)
**GET** `/api/contact/recent?limit=20`

Auth:
- Requires header: `x-admin-key: <ADMIN_API_KEY>`

Response (200):
```json
[
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "message": "string",
    "created_at": "2026-02-17T18:26:00.000Z"
  }
]
```

Errors:
- `401` if header missing/invalid

Backend implementation notes:
- Sort by `created_at` descending
- Apply `limit` (default 20, max 100)

---

## Backend configuration
- Add `ADMIN_API_KEY` to `backend/.env`
- Backend reads it via `os.environ.get("ADMIN_API_KEY")`

## Backend → Frontend switch
- Frontend must call backend using `process.env.REACT_APP_BACKEND_URL` + `/api` prefix
- Do not hardcode any URLs/ports
