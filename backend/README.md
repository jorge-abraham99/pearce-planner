# Backend Context

FastAPI backend for the Pearce delivery planner demo. It loads CSV files, schedules the current order book plus a new baler order, saves the new order back to CSV, and returns the generated schedule to the frontend.

## Main Files

- `app/main.py` - FastAPI app and route handlers.
- `app/csv_loader.py` - CSV loading, validation, and `orders.csv` append logic.
- `app/scheduler.py` - Scheduling engine and core assumptions.
- `app/models.py` - Pydantic request/response models.
- `app/settings.py` - Shared filesystem paths.
- `data/*.csv` - Demo data source tables.
- `tests/test_scheduler.py` - Scheduler regression tests.

## CSV Tables

`data/labour_requirements.csv`

Defines hours by baler type and stage:

```text
baler_type,stage,sequence_order,required_hours
```

Stages currently follow this order:

```text
press -> welding -> spraying -> assembling
```

`data/workers.csv`

Defines labour capacity:

```text
worker_id,worker_name,skill,hours_per_week
```

Daily capacity is calculated as:

```text
hours_per_week / 5
```

`data/orders.csv`

Current order book. New scheduled orders are appended here:

```text
order_id,baler_type,quantity,priority,status,earliest_completion_date,recommended_promise_date
```

`data/settings.csv`

Demo settings:

```text
start_date
planning_granularity
default_buffer_percentage
```

## API Endpoints

`GET /health`

Returns:

```json
{ "status": "ok" }
```

`GET /baler-types`

Returns available baler types from `labour_requirements.csv`.

`GET /tables`

Returns all CSV-backed source data for the UI.

`POST /schedule`

Request:

```json
{ "baler_type": "HB550" }
```

This calculates the new order schedule, appends the order to `orders.csv`, and returns:

- new order ID;
- earliest completion date;
- recommended promise date;
- bottleneck stage;
- assumptions;
- generated operation schedule;
- daily capacity usage.

## Scheduling Logic

The scheduler currently:

1. Loads existing orders.
2. Creates the next order ID, such as `O004`.
3. Appends the new order in memory.
4. Sorts all orders by ascending `priority`.
5. Rebuilds the schedule from `settings.start_date`.
6. Reserves daily capacity by skill.
7. Calculates completion and promise dates for the new order.
8. Saves the new order with those dates into `orders.csv`.

Important assumptions:

- Pressing uses `assembling` capacity. There is no separate press worker.
- Worker daily capacity is `hours_per_week / 5`.
- Each baler stage uses one worker's daily capacity at a time.
- Stages follow `sequence_order`.
- Stages may continue on the same day when time allows.
- Assembly starts the day after spraying.
- Existing orders consume capacity before lower-priority orders.
- Bottleneck is the stage with the most scheduled days, then most hours.
- The full operation schedule is recalculated each time; only order rows are persisted.

## Current Limitation

The app does not persist individual scheduled operations. `orders.csv` stores order-level completion and promise dates only. If labour requirements, workers, priorities, or start date change, old saved dates may no longer match a fresh recalculation unless they are backfilled.

## Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

## Test

```bash
cd backend
.venv/bin/python -m pytest
```
