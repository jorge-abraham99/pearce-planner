from datetime import date

from pydantic import BaseModel, ConfigDict


class ScheduleRequest(BaseModel):
    baler_type: str


class NewOrder(BaseModel):
    order_id: str
    baler_type: str


class ScheduledOperation(BaseModel):
    order_id: str
    baler_type: str
    stage: str
    scheduled_week: date
    required_hours: float


class CapacityUsage(BaseModel):
    week_start: date
    stage: str
    available_hours: float
    used_hours: float
    remaining_hours: float


class ScheduleResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    new_order: NewOrder
    earliest_completion_date: date
    recommended_promise_date: date
    bottleneck_stage: str
    assumptions: list[str]
    schedule: list[ScheduledOperation]
    capacity_usage: list[CapacityUsage]


class BalerTypesResponse(BaseModel):
    baler_types: list[str]


class TablesResponse(BaseModel):
    labour_requirements: list[dict]
    workers: list[dict]
    orders: list[dict]
    settings: dict[str, str]
