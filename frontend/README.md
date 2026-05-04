# Frontend Context

Next.js frontend for the Pearce delivery planner demo. It lets the user view the current order book, choose a baler type, schedule the next order, and inspect the generated schedule and source data.

## Main Files

- `src/app/page.tsx` - One-page app state and data flow.
- `src/app/layout.tsx` - Root layout and metadata.
- `src/app/globals.css` - App styling.
- `src/lib/api.ts` - API client for the FastAPI backend.
- `src/lib/types.ts` - TypeScript shapes matching backend JSON.
- `src/components/BalerSelector.tsx` - New order selector and submit button.
- `src/components/CurrentOrdersTable.tsx` - Current order book, including completion and promise dates.
- `src/components/ScheduleResult.tsx` - Main answer card.
- `src/components/ScheduleTable.tsx` - Generated daily operation schedule.
- `src/components/CapacityTable.tsx` - Daily capacity usage by skill.
- `src/components/DataTables.tsx` - CSV-backed planning assumptions.

## Data Flow

On page load:

```text
GET /baler-types
GET /tables
```

When the user schedules an order:

```text
POST /schedule
GET /tables
```

The second `GET /tables` refreshes the current order book after the backend appends the new row to `orders.csv`.

## Backend URL

The API base URL is set in `src/lib/api.ts`.

Default:

```text
http://localhost:8000
```

Override with:

```text
NEXT_PUBLIC_API_BASE_URL
```

## Current UI Sections

1. Header and short planner description.
2. Current order book.
3. New baler selector.
4. Result cards:
   - recommended promise date;
   - earliest completion date;
   - bottleneck.
5. Generated schedule table.
6. Daily capacity usage table.
7. Source data tables for labour requirements, workers, and settings.

## Important Behaviour

Scheduling is not a dry run. Clicking `Schedule order` calls `POST /schedule`, and the backend saves the new order into `backend/data/orders.csv`.

The current order table displays:

- order ID;
- baler type;
- quantity;
- priority;
- completion date;
- promise date;
- status.

## Run

```bash
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

## Build

```bash
cd frontend
npm run build
```

## Deploy

See `../DEPLOY.md`.

## Design Notes

This is an operational planning screen, not a marketing page. Keep changes practical:

- current order book should stay near the top;
- avoid hiding source assumptions;
- keep table labels aligned with daily scheduling;
- do not describe functionality in long in-app help text;
- prefer direct controls and compact operational layout.
