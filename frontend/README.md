# Placement Tracker — frontend

A static, no-build-step frontend (`index.html` + `style.css` + `app.js`) for the
FastAPI job/placement tracking backend.

## Run it

1. **Start the backend** as usual (`uvicorn app.app:app --reload`), with your
   Postgres DB up and `.env` filled in.
2. **Apply the three backend patches** in `backend-fixes/` (drop them over the
   matching files in your project):
   - `app/app.py` — adds CORS so the browser will actually let this frontend
     talk to `http://localhost:8000`. Without this every request will fail
     silently with a CORS error in the console.
   - `app/database.py` — was ignoring `DATABASE_HOST` from `.env` and always
     connecting to `localhost`.
   - `app/routes/companies.py` — `delete_company` referenced `company` before
     it was queried; would 500 every time an admin tried to delete a company.
3. **Serve the frontend** from any static server (opening `index.html`
   directly via `file://` will hit CORS/module issues in some browsers).
   Easiest options:
   - VS Code's "Live Server" extension, or
   - `python -m http.server 5500` from inside this folder, then visit
     `http://localhost:5500`.

   If you serve it from a different port, add that origin to
   `allow_origins` in `app/app.py`.
4. Open the app, register an account, and you're in.

## What it covers

- Register / sign in (JWT stored in `localStorage`)
- Browse companies visiting, apply with one click
- "My applications" — see status, change status, withdraw
- "File a new drive" — add a company (any signed-in user can, matching the
  current backend, which doesn't restrict this endpoint to admins)

## Known gaps (backend-side, not fixed here)

- `GET /users/me` doesn't return `role`, so the frontend can't tell who's an
  admin — the "Withdraw"/delete flows just surface the backend's 403 if you
  try something you're not allowed to do, rather than hiding the button
  ahead of time.
- No endpoint exists to edit a company or promote a user to admin.
- Company name/position/location aren't validated for length or uniqueness
  client-side beyond `required` — the backend's own unique constraint will
  reject true duplicates.

## Config

The only thing you should need to change is the top of `app.js`:

```js
const API_BASE_URL = "http://localhost:8000";
```
