from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

COUNTRY_DATA = json.loads((Path(__file__).resolve().parents[1] / "data" / "countries.json").read_text(encoding="utf-8"))

def country_settings(country_code: str) -> dict:
    country = COUNTRY_DATA.get(country_code.upper())
    if not country:
        raise ValueError("Choose a supported country of operation.")
    return country

def valid_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
        return value
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return "UTC"

def local_today(timezone_name: str) -> str:
    return datetime.now(ZoneInfo(valid_timezone(timezone_name))).date().isoformat()
