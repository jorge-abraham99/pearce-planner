# Pearce Delivery Date Planner

Lightweight demo for estimating the earliest credible delivery date for a new baler order from CSV-backed labour requirements, worker capacity, and a current order book. Scheduling an order appends it to `backend/data/orders.csv` with its calculated completion and promise dates.

## Structure

- `backend/` - FastAPI API, CSV loading, and Python scheduling engine.
- `frontend/` - Next.js one-page decision tool.
- `backend/data/` - Demo CSV source tables.

Detailed context:

- `backend/README.md`
- `frontend/README.md`
- `DEPLOY.md`

## Run Locally

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## API

- `GET /health`
- `GET /baler-types`
- `GET /tables`
- `POST /schedule` with `{ "baler_type": "HB550" }`; this schedules the order and saves it to `orders.csv`.

## Demo Rule Set

Orders are scheduled by priority, stages follow `sequence_order`, worker capacity is calculated as `hours_per_week / 5`, pressing consumes assembling capacity, and stages may continue on the same day when time allows. The recommended promise date adds the configured buffer.
