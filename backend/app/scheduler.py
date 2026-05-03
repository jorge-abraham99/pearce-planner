from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from math import ceil
from typing import Any


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def week_end(week_start: date) -> date:
    return week_start + timedelta(days=6)


def add_days(value: date, days: int) -> date:
    return value + timedelta(days=days)


def add_buffer_days(completion_date: date, total_required_hours: float, daily_capacity: dict[str, float], percentage: float) -> date:
    total_capacity = sum(daily_capacity.values())
    if total_capacity <= 0:
        return completion_date
    unbuffered_days = total_required_hours / total_capacity
    buffer_days = max(1, ceil(unbuffered_days * (percentage / 100)))
    return completion_date + timedelta(days=buffer_days)


def build_weekly_capacity(workers: list[dict[str, Any]]) -> dict[str, float]:
    capacity: dict[str, float] = defaultdict(float)
    for worker in workers:
        capacity[worker["skill"]] += float(worker["hours_per_week"])
    return dict(capacity)


def build_daily_capacity(workers: list[dict[str, Any]]) -> dict[str, float]:
    return {skill: hours / 5 for skill, hours in build_weekly_capacity(workers).items()}


def build_daily_stage_limits(workers: list[dict[str, Any]]) -> dict[str, float]:
    limits: dict[str, float] = defaultdict(float)
    for worker in workers:
        limits[worker["skill"]] = max(limits[worker["skill"]], float(worker["hours_per_week"]) / 5)
    return dict(limits)


def capacity_skill_for_stage(stage: str) -> str:
    if stage == "press":
        return "assembling"
    return stage


def get_baler_types(labour_requirements: list[dict[str, Any]]) -> list[str]:
    return sorted({row["baler_type"] for row in labour_requirements})


def build_next_order(baler_type: str, orders: list[dict[str, Any]]) -> dict[str, Any]:
    order_numbers = [
        int(order["order_id"][1:])
        for order in orders
        if isinstance(order.get("order_id"), str) and order["order_id"].startswith("O") and order["order_id"][1:].isdigit()
    ]
    next_order_number = max(order_numbers, default=0) + 1
    next_priority = max((int(order["priority"]) for order in orders), default=0) + 1
    return {
        "order_id": f"O{next_order_number:03d}",
        "baler_type": baler_type,
        "quantity": 1,
        "priority": next_priority,
        "status": "current",
    }


def group_requirements_by_baler(labour_requirements: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for requirement in labour_requirements:
        grouped[requirement["baler_type"]].append(requirement)

    return {
        baler_type: sorted(requirements, key=lambda row: int(row["sequence_order"]))
        for baler_type, requirements in grouped.items()
    }


def schedule_orders(
    orders: list[dict[str, Any]],
    labour_requirements: list[dict[str, Any]],
    daily_capacity: dict[str, float],
    daily_stage_limits: dict[str, float],
    settings: dict[str, str],
) -> dict[str, Any]:
    start_date = parse_date(settings["start_date"])
    requirements_by_baler = group_requirements_by_baler(labour_requirements)
    used_capacity: dict[tuple[date, str], float] = defaultdict(float)
    schedule: list[dict[str, Any]] = []
    completion_dates: dict[str, date] = {}

    sorted_orders = sorted(orders, key=lambda row: (int(row["priority"]), row["order_id"]))
    for order in sorted_orders:
        baler_type = order["baler_type"]
        if baler_type not in requirements_by_baler:
            raise ValueError(f"Unknown baler type: {baler_type}")

        current_date = start_date
        elapsed_hours_used = 0.0
        elapsed_day_limit: float | None = None
        last_scheduled_date = start_date

        requirements = requirements_by_baler[baler_type]
        for requirement_index, requirement in enumerate(requirements):
            stage = requirement["stage"]
            skill = capacity_skill_for_stage(stage)
            available_hours = daily_capacity.get(skill, 0)
            stage_daily_limit = daily_stage_limits.get(skill, 0)
            remaining_hours = float(requirement["required_hours"]) * int(order.get("quantity", 1))
            if available_hours <= 0 or stage_daily_limit <= 0:
                raise ValueError(f"No daily capacity configured for stage: {stage}")

            while remaining_hours > 0:
                if elapsed_day_limit is None:
                    elapsed_day_limit = stage_daily_limit

                remaining_skill_capacity = available_hours - used_capacity[(current_date, skill)]
                remaining_elapsed_day = elapsed_day_limit - elapsed_hours_used
                if remaining_skill_capacity <= 0 or remaining_elapsed_day <= 0:
                    current_date = add_days(current_date, 1)
                    elapsed_hours_used = 0
                    elapsed_day_limit = None
                    continue

                scheduled_hours = min(
                    remaining_hours,
                    remaining_skill_capacity,
                    stage_daily_limit,
                    remaining_elapsed_day,
                )
                if scheduled_hours <= 0:
                    raise ValueError(f"Unable to schedule stage: {stage}")

                used_capacity[(current_date, skill)] += scheduled_hours
                elapsed_hours_used += scheduled_hours
                remaining_hours -= scheduled_hours
                last_scheduled_date = current_date
                schedule.append(
                    {
                        "order_id": order["order_id"],
                        "baler_type": baler_type,
                        "stage": stage,
                        "scheduled_week": current_date,
                        "required_hours": scheduled_hours,
                    }
                )

            if stage == "spraying" and requirement_index < len(requirements) - 1:
                current_date = add_days(current_date, 1)
                elapsed_hours_used = 0
                elapsed_day_limit = None

        completion_dates[order["order_id"]] = last_scheduled_date

    capacity_usage = build_capacity_usage(used_capacity, daily_capacity)
    return {
        "schedule": schedule,
        "capacity_usage": capacity_usage,
        "completion_dates": completion_dates,
        "bottleneck_stage": identify_bottleneck(schedule),
    }


def build_capacity_usage(
    used_capacity: dict[tuple[date, str], float],
    daily_capacity: dict[str, float],
) -> list[dict[str, Any]]:
    rows = []
    for (week_start, stage), used_hours in sorted(used_capacity.items(), key=lambda item: (item[0][0], item[0][1])):
        available_hours = daily_capacity[stage]
        rows.append(
            {
                "week_start": week_start,
                "stage": stage,
                "available_hours": available_hours,
                "used_hours": used_hours,
                "remaining_hours": available_hours - used_hours,
            }
        )
    return rows


def identify_bottleneck(schedule: list[dict[str, Any]]) -> str:
    days_by_stage: dict[str, set[date]] = defaultdict(set)
    hours_by_stage: dict[str, float] = defaultdict(float)
    for row in schedule:
        days_by_stage[row["stage"]].add(row["scheduled_week"])
        hours_by_stage[row["stage"]] += row["required_hours"]

    if not days_by_stage:
        return "unknown"

    return max(
        days_by_stage,
        key=lambda stage: (len(days_by_stage[stage]), hours_by_stage[stage]),
    )


def schedule_new_order(
    baler_type: str,
    labour_requirements: list[dict[str, Any]],
    workers: list[dict[str, Any]],
    orders: list[dict[str, Any]],
    settings: dict[str, str],
) -> dict[str, Any]:
    baler_types = get_baler_types(labour_requirements)
    if baler_type not in baler_types:
        allowed = ", ".join(baler_types)
        raise ValueError(f"Unknown baler type '{baler_type}'. Allowed values: {allowed}")

    new_order = build_next_order(baler_type, orders)
    all_orders = [*orders, new_order]
    daily_capacity = build_daily_capacity(workers)
    daily_stage_limits = build_daily_stage_limits(workers)
    scheduled = schedule_orders(all_orders, labour_requirements, daily_capacity, daily_stage_limits, settings)

    earliest_completion_date = scheduled["completion_dates"][new_order["order_id"]]
    requirements_by_baler = group_requirements_by_baler(labour_requirements)
    total_required_hours = sum(float(row["required_hours"]) for row in requirements_by_baler[baler_type])
    buffer_percentage = float(settings.get("default_buffer_percentage", 0))
    recommended_promise_date = add_buffer_days(
        earliest_completion_date,
        total_required_hours,
        daily_capacity,
        buffer_percentage,
    )
    new_order["earliest_completion_date"] = earliest_completion_date.isoformat()
    new_order["recommended_promise_date"] = recommended_promise_date.isoformat()

    return {
        "new_order": {
            "order_id": new_order["order_id"],
            "baler_type": baler_type,
        },
        "order_to_save": new_order,
        "earliest_completion_date": earliest_completion_date,
        "recommended_promise_date": recommended_promise_date,
        "bottleneck_stage": scheduled["bottleneck_stage"],
        "assumptions": [
            "New order added to the current order book",
            "Worker capacity calculated as hours per week divided by 5",
            "Pressing uses assembling labour capacity",
            "Each baler stage uses one worker's daily capacity at a time",
            "Assembly starts the day after spraying",
            f"{buffer_percentage:g}% buffer applied",
            "Stages follow sequence order and may continue on the same day when time allows",
        ],
        "schedule": scheduled["schedule"],
        "capacity_usage": scheduled["capacity_usage"],
    }
