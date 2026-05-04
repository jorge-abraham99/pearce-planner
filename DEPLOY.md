# Fly.io Deployment

This repo deploys cleanly as two Fly apps:

- backend FastAPI app;
- frontend Next.js app.

Each app has its own `Dockerfile` and `fly.toml`.

## Important

The backend writes scheduled orders to `orders.csv`. Fly Machine root filesystems are ephemeral, so the backend `fly.toml` mounts a Fly Volume at `/data`.

On first boot, `backend/start.sh` seeds `/data` from the CSV files bundled into the image if `/data/orders.csv` does not exist yet.

## Default App Names

The checked-in configs use:

```text
pearce-planner-backend
pearce-planner-frontend
```

Fly app names are globally unique. If either name is taken, choose your own names and update:

- `backend/fly.toml`:
  - `app`
  - `ALLOWED_ORIGINS`
- `frontend/fly.toml`:
  - `app`
  - `NEXT_PUBLIC_API_BASE_URL`

## Backend

From the repo root:

```bash
fly apps create pearce-planner-backend
fly volumes create pearce_data --app pearce-planner-backend --region lhr --size 1
fly deploy ./backend --app pearce-planner-backend
```

Health check:

```bash
curl https://pearce-planner-backend.fly.dev/health
```

Expected:

```json
{ "status": "ok" }
```

## Frontend

From the repo root:

```bash
fly apps create pearce-planner-frontend
fly deploy ./frontend --app pearce-planner-frontend
```

Open:

```text
https://pearce-planner-frontend.fly.dev
```

## If You Use Different App Names

Example:

```text
my-pearce-api.fly.dev
my-pearce-web.fly.dev
```

Set backend CORS in `backend/fly.toml`:

```toml
ALLOWED_ORIGINS = "https://my-pearce-web.fly.dev"
```

Set frontend API URL in `frontend/fly.toml`:

```toml
NEXT_PUBLIC_API_BASE_URL = "https://my-pearce-api.fly.dev"
```

Then redeploy both apps.

## Why Two Apps?

The frontend is a browser-facing Next.js app. The backend is a FastAPI service with writable CSV data. Keeping them separate makes the API URL, CORS, storage, and scaling easier to reason about.

## Caveat

CSV persistence on a Fly Volume is fine for this demo, but it is not a long-term multi-user database. If this planner becomes real workflow software, move the order book and generated schedule into Postgres.
