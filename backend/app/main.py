from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.csv_loader import append_order, load_all_tables, load_labour_requirements, load_orders, load_settings, load_workers
from app.models import BalerTypesResponse, ScheduleRequest, ScheduleResult, TablesResponse
from app.scheduler import get_baler_types, schedule_new_order
from app.settings import get_allowed_origins


app = FastAPI(title="Pearce Delivery Date Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/baler-types", response_model=BalerTypesResponse)
def baler_types() -> BalerTypesResponse:
    return BalerTypesResponse(baler_types=get_baler_types(load_labour_requirements()))


@app.get("/tables", response_model=TablesResponse)
def tables() -> dict:
    return load_all_tables()


@app.post("/schedule", response_model=ScheduleResult)
def schedule(request: ScheduleRequest) -> dict:
    try:
        result = schedule_new_order(
            baler_type=request.baler_type,
            labour_requirements=load_labour_requirements(),
            workers=load_workers(),
            orders=load_orders(),
            settings=load_settings(),
        )
        append_order(result.pop("order_to_save"))
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
