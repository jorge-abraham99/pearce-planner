from __future__ import annotations

import csv
from datetime import date
from typing import Any

from app.settings import DATA_DIR


ORDER_COLUMNS = [
    "order_id",
    "baler_type",
    "quantity",
    "priority",
    "status",
    "earliest_completion_date",
    "recommended_promise_date",
]

SETTING_COLUMNS = ["setting", "value"]


class CSVValidationError(ValueError):
    """Raised when a source CSV is missing required demo columns."""


def _load_csv(filename: str, required_columns: set[str]) -> list[dict[str, str]]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV data file: {path}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = required_columns - fieldnames
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise CSVValidationError(f"{filename} is missing columns: {missing_list}")
        return [
            dict(row)
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]


def load_labour_requirements() -> list[dict[str, Any]]:
    rows = _load_csv(
        "labour_requirements.csv",
        {"baler_type", "stage", "sequence_order", "required_hours"},
    )
    return [
        {
            "baler_type": row["baler_type"],
            "stage": row["stage"],
            "sequence_order": int(row["sequence_order"]),
            "required_hours": float(row["required_hours"]),
        }
        for row in rows
    ]


def load_workers() -> list[dict[str, Any]]:
    rows = _load_csv(
        "workers.csv",
        {"worker_id", "worker_name", "skill", "hours_per_week"},
    )
    return [
        {
            "worker_id": row["worker_id"],
            "worker_name": row["worker_name"],
            "skill": row["skill"],
            "hours_per_week": float(row["hours_per_week"]),
        }
        for row in rows
    ]


def load_orders() -> list[dict[str, Any]]:
    rows = _load_csv("orders.csv", set(ORDER_COLUMNS))
    return [
        {
            "order_id": row["order_id"],
            "baler_type": row["baler_type"],
            "quantity": int(row["quantity"]),
            "priority": int(row["priority"]),
            "status": row["status"],
            "earliest_completion_date": row.get("earliest_completion_date", ""),
            "recommended_promise_date": row.get("recommended_promise_date", ""),
        }
        for row in rows
    ]


def append_order(order: dict[str, Any]) -> None:
    path = DATA_DIR / "orders.csv"
    file_has_rows = path.exists() and path.stat().st_size > 0

    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ORDER_COLUMNS)
        if not file_has_rows:
            writer.writeheader()
        writer.writerow({column: order.get(column, "") for column in ORDER_COLUMNS})


def save_orders(orders: list[dict[str, Any]]) -> None:
    path = DATA_DIR / "orders.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ORDER_COLUMNS)
        writer.writeheader()
        for order in orders:
            writer.writerow({column: order.get(column, "") for column in ORDER_COLUMNS})


def delete_order(order_id: str) -> None:
    orders = load_orders()
    remaining_orders = [order for order in orders if order["order_id"] != order_id]
    if len(remaining_orders) == len(orders):
        raise ValueError(f"Unknown order ID: {order_id}")
    save_orders(remaining_orders)


def load_settings() -> dict[str, str]:
    rows = _load_csv("settings.csv", {"setting", "value"})
    return {row["setting"]: row["value"] for row in rows}


def save_settings(settings: dict[str, str]) -> None:
    path = DATA_DIR / "settings.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SETTING_COLUMNS)
        writer.writeheader()
        for setting, value in settings.items():
            writer.writerow({"setting": setting, "value": value})


def update_start_date(start_date: date) -> dict[str, str]:
    settings = load_settings()
    settings["start_date"] = start_date.isoformat()
    save_settings(settings)
    return settings


def load_all_tables() -> dict[str, Any]:
    return {
        "labour_requirements": load_labour_requirements(),
        "workers": load_workers(),
        "orders": load_orders(),
        "settings": load_settings(),
    }
