# Pearce Baler Scheduling Demo — Build Plan

## 1. Goal

Build a lightweight demo that answers one question:

> Given the current order book and known labour capacity, what is the earliest credible delivery date for a new baler order?

The demo should keep user input minimal. The user should only need to select the baler type for the new order. Everything else should be loaded from predefined CSV tables.

The product should feel like a simple planning decision tool, not a full ERP or production planning system.

---

## 2. Proposed Architecture

Use:

- **Next.js** for the frontend UI.
- **FastAPI** for the backend API.
- **Python** for scheduling logic and CSV processing.
- **CSV files** as temporary table-like data sources for the demo.
- **Fly.io** later for deployment.

High-level flow:

```text
CSV files
  ↓
FastAPI backend
  ↓
Python scheduling engine
  ↓
API response
  ↓
Next.js UI
```

For the demo, there is no database. The backend reads CSV files, builds an in-memory schedule, calculates the delivery estimate, and returns the result to the UI.

---

## 3. Repository Structure

Recommended monorepo structure:

```text
pearce-planner/
  README.md
  Plan.md

  frontend/
    package.json
    next.config.js
    src/
      app/
        page.tsx
        layout.tsx
      components/
        BalerSelector.tsx
        DataTables.tsx
        ScheduleResult.tsx
        CapacityTable.tsx
        ScheduleTable.tsx
      lib/
        api.ts
        types.ts

  backend/
    pyproject.toml
    requirements.txt
    app/
      main.py
      models.py
      csv_loader.py
      scheduler.py
      settings.py
    data/
      labour_requirements.csv
      workers.csv
      orders.csv
      settings.csv
    tests/
      test_scheduler.py
```

---

## 4. Core Demo Principle

The demo input should only be:

```text
New order baler type
```

Example:

```text
HB550
HB60
SC3000
MC32STD
```

The app should already know:

- labour hours by baler type;
- production stages;
- stage order;
- worker capacity by skill;
- current order book;
- planning start date;
- buffer assumption.

---

## 5. CSV Tables

For the demo, CSVs act as the source tables.

### 5.1 `labour_requirements.csv`

Purpose: defines labour demand for each baler type.

```csv
baler_type,stage,sequence_order,required_hours
HB550,press,1,10
HB550,welding,2,24
HB550,spraying,3,6
HB550,assembling,4,18
HB60,press,1,12
HB60,welding,2,30
HB60,spraying,3,8
HB60,assembling,4,22
SC3000,press,1,16
SC3000,welding,2,45
SC3000,spraying,3,10
SC3000,assembling,4,30
MC32STD,press,1,8
MC32STD,welding,2,20
MC32STD,spraying,3,5
MC32STD,assembling,4,16
```

Fields:

| Field | Meaning |
|---|---|
| `baler_type` | Product type, e.g. HB550 |
| `stage` | Production stage |
| `sequence_order` | Order in which stages must happen |
| `required_hours` | Labour hours needed for that stage |

---

### 5.2 `workers.csv`

Purpose: defines labour supply.

```csv
worker_id,worker_name,skill,hours_per_week
W1,Welder 1,welding,40
W2,Welder 2,welding,32
S1,Sprayer 1,spraying,40
P1,Press 1,press,40
A1,Assembler 1,assembling,40
```

Fields:

| Field | Meaning |
|---|---|
| `worker_id` | Unique worker identifier |
| `worker_name` | Human-readable worker label |
| `skill` | Skill / production stage the worker contributes to |
| `hours_per_week` | Available weekly hours |

For the demo, assume one skill per worker. Later, this can be normalised into `workers` and `worker_skills`.

---

### 5.3 `orders.csv`

Purpose: defines the existing order book.

```csv
order_id,baler_type,quantity,priority,status
O001,HB550,1,1,current
O002,SC3000,1,2,current
O003,HB60,1,3,current
```

Fields:

| Field | Meaning |
|---|---|
| `order_id` | Unique order identifier |
| `baler_type` | Baler type |
| `quantity` | Number of balers in order |
| `priority` | Lower number means higher priority |
| `status` | `current` or `proposed` |

The proposed order should not need to exist in the CSV. The backend creates it in memory when the user selects a baler type.

---

### 5.4 `settings.csv`

Purpose: stores simple demo assumptions.

```csv
setting,value
start_date,2026-06-01
planning_granularity,week
default_buffer_percentage,10
```

Fields:

| Field | Meaning |
|---|---|
| `start_date` | First week/date to schedule from |
| `planning_granularity` | For demo, use `week` |
| `default_buffer_percentage` | Buffer added to recommended promise date |

---

## 6. Scheduling Logic

### 6.1 Inputs

The scheduling engine receives:

- `labour_requirements`
- `workers`
- `orders`
- `settings`
- `new_order_baler_type`

### 6.2 Outputs

The engine returns:

- earliest feasible completion date for the new order;
- recommended promise date with buffer;
- bottleneck stage;
- full generated schedule;
- weekly capacity usage;
- assumptions used.

### 6.3 Scheduling Algorithm — Version 1

Use a simple weekly capacity model.

Steps:

```text
1. Load current orders.
2. Create a proposed order using selected baler type.
3. Append proposed order to the order list.
4. Sort orders by priority.
5. Calculate weekly available capacity by skill from workers.csv.
6. For each order:
   a. Look up required stages for its baler type.
   b. Sort stages by sequence_order.
   c. For each stage:
      i. Find the earliest week at or after the previous stage's scheduled week.
      ii. Check if that week's skill capacity has enough remaining hours.
      iii. If enough capacity exists, reserve the hours.
      iv. If not, move to the next week and retry.
   d. Completion date is the end of the final scheduled stage week.
7. Identify the proposed order's completion date.
8. Add buffer to get recommended promise date.
9. Identify bottleneck based on most constrained skill/capacity ratio.
```

### 6.4 Conservative Assumption

For the first demo, use this conservative rule:

> Each production stage must be scheduled no earlier than the week after the previous stage.

Example:

```text
Week 1: press
Week 2: welding
Week 3: spraying
Week 4: assembling
```

This is easier to explain and avoids false precision.

Later, we can allow same-week stage progression if needed.

---

## 7. Backend Plan — FastAPI

### 7.1 Main Responsibilities

The FastAPI backend should:

- load CSV data;
- validate required columns;
- expose API endpoints for the frontend;
- run scheduling logic;
- return JSON responses.

### 7.2 Backend Modules

#### `main.py`

FastAPI app and route definitions.

#### `csv_loader.py`

Loads and validates CSV files.

Functions:

```python
def load_labour_requirements():
    ...

def load_workers():
    ...

def load_orders():
    ...

def load_settings():
    ...
```

#### `models.py`

Pydantic request and response models.

Useful models:

```python
class ScheduleRequest(BaseModel):
    baler_type: str

class ScheduleResult(BaseModel):
    baler_type: str
    earliest_completion_date: date
    recommended_promise_date: date
    bottleneck_stage: str
    assumptions: list[str]
    schedule: list[ScheduledOperation]
    capacity_usage: list[CapacityUsage]
```

#### `scheduler.py`

Core scheduling logic.

Useful functions:

```python
def build_weekly_capacity(workers):
    ...

def schedule_orders(orders, labour_requirements, capacity, settings):
    ...

def schedule_new_order(baler_type):
    ...
```

---

## 8. Backend API Endpoints

### 8.1 Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

### 8.2 Get Baler Types

```http
GET /baler-types
```

Response:

```json
{
  "baler_types": ["HB550", "HB60", "SC3000", "MC32STD"]
}
```

---

### 8.3 Get Input Tables

```http
GET /tables
```

Response:

```json
{
  "labour_requirements": [...],
  "workers": [...],
  "orders": [...],
  "settings": {...}
}
```

Used by the UI to show the data powering the model.

---

### 8.4 Schedule New Order

```http
POST /schedule
```

Request:

```json
{
  "baler_type": "HB550"
}
```

Response:

```json
{
  "new_order": {
    "order_id": "NEW001",
    "baler_type": "HB550"
  },
  "earliest_completion_date": "2026-07-20",
  "recommended_promise_date": "2026-07-27",
  "bottleneck_stage": "welding",
  "assumptions": [
    "Current order book unchanged",
    "Standard weekly worker availability used",
    "10% buffer applied",
    "Each stage scheduled no earlier than the following week"
  ],
  "schedule": [
    {
      "order_id": "O001",
      "baler_type": "HB550",
      "stage": "press",
      "scheduled_week": "2026-06-01",
      "required_hours": 10
    }
  ],
  "capacity_usage": [
    {
      "week_start": "2026-06-01",
      "stage": "welding",
      "available_hours": 72,
      "used_hours": 54,
      "remaining_hours": 18
    }
  ]
}
```

---

## 9. Frontend Plan — Next.js

### 9.1 Main Page

The main UI should be one page with four sections:

```text
1. Select new baler type
2. Scheduling result
3. Generated schedule table
4. Input data tables
```

---

### 9.2 Components

#### `BalerSelector.tsx`

Purpose: lets user select one baler type and submit.

UI:

```text
What baler type is the customer asking for?
[ HB550 ▼ ]
[ Calculate delivery date ]
```

---

#### `ScheduleResult.tsx`

Purpose: shows the commercial answer.

Should display:

```text
Earliest feasible completion: 2026-07-20
Recommended promise date: 2026-07-27
Main bottleneck: Welding
```

Also show assumptions:

```text
- Current order book unchanged
- Standard weekly worker availability used
- 10% buffer applied
```

---

#### `CapacityTable.tsx`

Purpose: shows capacity by week and stage.

Example columns:

| Week | Stage | Available | Used | Remaining |
|---|---|---:|---:|---:|
| 2026-06-01 | welding | 72 | 54 | 18 |

---

#### `ScheduleTable.tsx`

Purpose: shows generated schedule.

Example columns:

| Order | Baler Type | Stage | Week | Required Hours |
|---|---|---|---|---:|
| O001 | HB550 | press | 2026-06-01 | 10 |

---

#### `DataTables.tsx`

Purpose: shows the raw CSV-backed data so the demo is transparent.

Tables:

- labour requirements;
- workers;
- current orders;
- settings.

---

## 10. Frontend Data Flow

```text
Page loads
  ↓
GET /baler-types
  ↓
GET /tables
  ↓
User selects baler type
  ↓
POST /schedule
  ↓
Render result, schedule table, capacity table
```

---

## 11. Suggested UI Copy

### Header

```text
Pearce Delivery Date Planner
```

### Subheader

```text
Select a baler type to estimate the earliest credible delivery date against the current order book and available labour capacity.
```

### Result Card

```text
Recommended Promise Date
2026-07-27

Earliest Feasible Completion
2026-07-20

Main Bottleneck
Welding
```

### Transparency Note

```text
This result is calculated from the current order book, stage-level labour requirements, and weekly worker capacity. The schedule resets each time the demo is run.
```

---

## 12. Development Milestones

### Milestone 1 — Define CSVs

Create demo CSV files:

- `labour_requirements.csv`
- `workers.csv`
- `orders.csv`
- `settings.csv`

Acceptance criteria:

- CSVs contain all required columns.
- All four baler types exist.
- All four stages exist for every baler type.

---

### Milestone 2 — Build Scheduling Engine Locally

Implement `scheduler.py`.

Acceptance criteria:

- Can load CSVs.
- Can calculate weekly capacity by stage.
- Can schedule existing orders.
- Can add a proposed order by baler type.
- Can return completion date and bottleneck.

---

### Milestone 3 — Build FastAPI Endpoints

Implement:

- `GET /health`
- `GET /baler-types`
- `GET /tables`
- `POST /schedule`

Acceptance criteria:

- API returns valid JSON.
- API handles invalid baler type gracefully.
- API response includes result, schedule, capacity usage, and assumptions.

---

### Milestone 4 — Build Next.js UI

Implement one-page UI.

Acceptance criteria:

- User can select baler type.
- User can click calculate.
- UI shows recommended promise date.
- UI shows bottleneck.
- UI shows generated schedule and capacity usage.
- UI shows input tables.

---

### Milestone 5 — Local End-to-End Demo

Run frontend and backend locally.

Acceptance criteria:

- Next.js calls FastAPI successfully.
- Selecting each of the four baler types returns a result.
- Results are understandable to a non-technical user.

---

### Milestone 6 — Deploy to Fly.io

Deploy backend and frontend.

Options:

1. Deploy as two Fly apps:
   - `pearce-planner-frontend`
   - `pearce-planner-backend`

2. Or deploy as one combined app if using a reverse proxy or serving frontend statically.

For simplicity during demo, two apps may be cleaner.

Acceptance criteria:

- Public frontend URL works.
- Frontend can call backend API.
- CSV files are bundled read-only with backend deployment.
- Demo resets on each schedule run or deploy.

---

## 13. Initial Scheduling Rules

Use these rules for version 1:

1. Orders are scheduled by ascending priority.
2. New proposed order is added after current orders by default.
3. Stages are scheduled in `sequence_order`.
4. Each stage needs capacity from the matching worker skill.
5. Capacity is calculated weekly.
6. A stage is scheduled in the earliest week with enough remaining capacity.
7. The next stage starts no earlier than the following week.
8. Completion date is the end of the week of the final stage.
9. Recommended promise date is completion date plus buffer.
10. Bottleneck is the stage with the highest average utilisation across the generated schedule.

---

## 14. Known Simplifications

The first demo does **not** handle:

- daily scheduling;
- partial stage work split across weeks;
- people with multiple skills;
- holidays or absences;
- overtime scenarios;
- material delays;
- rework;
- manual priority overrides in the UI;
- persisted user edits;
- database storage;
- machine capacity;
- ML forecasting.

These are acceptable omissions for the demo.

---

## 15. Future Improvements

After the demo, add capabilities in this order:

1. CSV upload in the UI.
2. Worker availability exceptions.
3. Overtime toggle.
4. Manual priority changes.
5. Same-week stage progression.
6. Partial work split across weeks.
7. Work log / actuals table.
8. Postgres database.
9. Authentication.
10. Simple admin interface.
11. Historical forecasting.
12. ML-based delivery confidence once enough data exists.

---

## 16. Recommended First Build Scope

Build only this first:

```text
Next.js UI:
- baler type selector
- result card
- schedule table
- capacity table
- raw input tables

FastAPI backend:
- CSV loading
- schedule endpoint
- simple scheduling engine
```

Do not build persistence yet. The demo should be deterministic and resettable.

---

## 17. Success Criteria

The demo succeeds if it can show:

1. A user selects `HB550`, `HB60`, `SC3000`, or `MC32STD`.
2. The app calculates a credible delivery date.
3. The app explains the bottleneck.
4. The app shows the schedule behind the answer.
5. The app shows the input data used.
6. The logic is simple enough to explain to Steve and Andy.

The ideal demo message is:

> “For now, the user only selects the baler type. The app uses preloaded labour requirements, worker capacity, and the current order book to generate a temporary schedule and a recommended promise date. This proves the planning logic before we introduce a database or heavier workflow.”
