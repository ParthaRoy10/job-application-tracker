# Deploying Placement Tracker

Two independent pieces: a FastAPI service (needs Postgres) and a static
frontend (needs nothing but a CDN). This guide uses **Render** for the
backend + database and **Netlify** for the frontend — both have free tiers
and no credit card required, which suits a portfolio project. Railway or
Fly.io work the same way if you'd rather use those.

## 0. Before you deploy — clean up secrets

Your `.env` is already git-ignored and never got committed, which is the
important part. Still, rotate the values in it now rather than later:

- `DATABASE_PASSWORD` — pick a new one, it's going into Render's dashboard
  anyway, not into git.
- `JWT_SECRET_KEY` — generate a real one:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

Add a `.env.example` (no real values) to the repo so anyone cloning it knows
what to set:

```
DATABASE_NAME=job_tracker
DATABASE_USER=jobtracker
DATABASE_PASSWORD=
DATABASE_PORT=5432
DATABASE_HOST=localhost

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## 1. Push the repo to GitHub

```bash
cd /path/to/your/project
git add app.py database.py routes/companies.py frontend/ docs/ alembic/ \
        requirements.txt README.md DEPLOYMENT.md .env.example
git commit -m "docs: add architecture writeup, requirements.txt, deployment guide"

# first time only
gh repo create placement-tracker --public --source=. --remote=origin
git push -u origin main
```

(No `gh`? Create the repo on github.com first, then
`git remote add origin git@github.com:<you>/placement-tracker.git`.)

## 2. Backend + database on Render

1. **New → PostgreSQL** on Render. Note the internal connection details it
   gives you (host, port, database, user, password).
2. **New → Web Service**, connect your GitHub repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.app:app --host 0.0.0.0 --port $PORT`
3. Under the service's **Environment** tab, add:
   - `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`,
     `DATABASE_PASSWORD` — from the Postgres instance in step 1
   - `JWT_SECRET_KEY`, `JWT_ALGORITHM=HS256`,
     `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120`
4. **Run migrations against the production DB** — either add a Render "pre-deploy
   command" of `alembic upgrade head`, or run it once locally pointed at the
   production `DATABASE_URL`.
5. Deploy. You'll get a URL like `https://placement-tracker-api.onrender.com`
   — hit `/` in a browser to confirm you see the welcome message.

## 3. Lock down CORS for production

The `allow_origin_regex` matching any `localhost` port was for local dev
only. Once you know your frontend's real URL, tighten it:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://placement-tracker.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit that change and push — Render redeploys automatically.

## 4. Frontend on Netlify

1. **Add new site → Import from GitHub**, pick the repo, set the **base
   directory** to `frontend/` (no build command needed — it's static).
2. Before deploying, update `frontend/app.js`:
   ```js
   const API_BASE_URL = "https://placement-tracker-api.onrender.com";
   ```
   Commit and push; Netlify redeploys on every push to `main`.
3. Netlify gives you a URL like `https://placement-tracker.netlify.app` —
   that's the exact value to put in step 3's `allow_origins`.

## 5. Sanity check

- Open the Netlify URL, register a user, apply to a company, change a
  status, withdraw it. Watch Render's logs while you do it — a 401 means the
  token isn't being sent or has expired; a CORS error in the browser console
  means step 3's origin doesn't exactly match the Netlify URL (scheme +
  host, no trailing slash).
- Render's free tier spins the service down after inactivity, so the first
  request after a while will be slow (10–30s) as it wakes back up — normal,
  not a bug.
