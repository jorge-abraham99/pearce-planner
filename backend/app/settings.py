import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))


def get_allowed_origins() -> list[str]:
    configured_origins = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *origins,
    ]
