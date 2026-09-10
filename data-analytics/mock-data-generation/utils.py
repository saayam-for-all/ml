"""Helpers for Virginia analytics mock-data generation (#301)."""

from __future__ import annotations

import csv
import json
import math
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

DEFAULT_SEED = 42
DEFAULT_ROWS = 400
TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"
EXAMPLE_TS = "2026-08-31 14:30:00"

FIRST_NAMES = (
    "Avery", "Jordan", "Riley", "Casey", "Quinn", "Morgan", "Reese", "Skyler",
    "Cameron", "Hayden", "Parker", "Drew", "Sage", "Rowan", "Finley", "Blake",
)
LAST_NAMES = (
    "Harbor", "Meadow", "Pine", "Willow", "Cedar", "Brook", "Ridge", "Field",
    "Grove", "Valley", "Summit", "Lake", "Dale", "Glen", "Shore", "Creek",
)
ORG_PREFIXES = (
    "Harbor", "Cedar", "Valley", "Ridge", "Meadow", "Summit", "Brook", "Grove",
)
ORG_SUFFIXES = (
    "Mutual Aid", "Community Pantry", "Literacy Circle", "Care Collective",
    "Youth Network", "Housing Alliance", "Wellness Hub", "Skills Workshop",
)
MISSIONS = (
    "Food assistance and grocery support for local families.",
    "Education and tutoring for students who need extra help.",
    "Housing navigation and emergency shelter coordination.",
    "Healthcare access guidance and wellness workshops.",
    "Clothing and essentials distribution for new arrivals.",
    "Elder support, errands, and community connection.",
)
ORG_TYPES = ("Non-Profit", "For-profit")
ORG_SIZES = ("Small", "Medium", "Large")
ORG_SOURCES = ("manual", "genai")
LANGUAGES = ("English", "Spanish", "Hindi", "French", "Arabic")
TIMEZONES = (
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "Europe/Dublin",
    "Asia/Kolkata",
)
GENDERS = ("Female", "Male", "Non-binary", "Prefer not to say")

# Public geographic centroids used only to keep country → state → city → coords
# consistent. Personally identifiable user data is never taken from live CSVs.
GEO_SEEDS = (
    {
        "country_name": "United States",
        "country_code": "USA",
        "phone_code": "1",
        "is_eu_member": False,
        "state_name": "California",
        "state_code": "CA",
        "city_name": "San Jose",
        "lat": 37.3382,
        "lon": -121.8863,
        "zip_code": "95112",
        "time_zone": "America/Los_Angeles",
    },
    {
        "country_name": "United States",
        "country_code": "USA",
        "phone_code": "1",
        "is_eu_member": False,
        "state_name": "Virginia",
        "state_code": "VA",
        "city_name": "Ashburn",
        "lat": 39.0438,
        "lon": -77.4874,
        "zip_code": "20147",
        "time_zone": "America/New_York",
    },
    {
        "country_name": "United States",
        "country_code": "USA",
        "phone_code": "1",
        "is_eu_member": False,
        "state_name": "Texas",
        "state_code": "TX",
        "city_name": "Austin",
        "lat": 30.2672,
        "lon": -97.7431,
        "zip_code": "78701",
        "time_zone": "America/Chicago",
    },
    {
        "country_name": "India",
        "country_code": "IND",
        "phone_code": "91",
        "is_eu_member": False,
        "state_name": "Karnataka",
        "state_code": "KA",
        "city_name": "Bengaluru",
        "lat": 12.9716,
        "lon": 77.5946,
        "zip_code": "560001",
        "time_zone": "Asia/Kolkata",
    },
    {
        "country_name": "Ireland",
        "country_code": "IRL",
        "phone_code": "353",
        "is_eu_member": True,
        "state_name": "Leinster",
        "state_code": "L",
        "city_name": "Dublin",
        "lat": 53.3498,
        "lon": -6.2603,
        "zip_code": "D02",
        "time_zone": "Europe/Dublin",
    },
    {
        "country_name": "Canada",
        "country_code": "CAN",
        "phone_code": "1",
        "is_eu_member": False,
        "state_name": "Ontario",
        "state_code": "ON",
        "city_name": "Toronto",
        "lat": 43.6532,
        "lon": -79.3832,
        "zip_code": "M5V",
        "time_zone": "America/Toronto",
    },
)


def set_seed(seed: int = DEFAULT_SEED) -> None:
    random.seed(seed)


def format_ts(value: datetime) -> str:
    return value.strftime(TIMESTAMP_FMT)


def format_date(value: datetime) -> str:
    return value.strftime(DATE_FMT)


def json_text(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, TIMESTAMP_FMT)


def ewkt_point(lon: float, lat: float) -> str:
    return f"SRID=4326;POINT({lon:.6f} {lat:.6f})"


def parse_ewkt_point(value: str) -> tuple[float, float]:
    match = re.search(r"POINT\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", value or "")
    if not match:
        raise ValueError(f"Not a POINT geography: {value!r}")
    lon, lat = float(match.group(1)), float(match.group(2))
    return lon, lat


def jitter_coord(lat: float, lon: float, scale: float = 0.08) -> tuple[float, float]:
    return (
        max(-90.0, min(90.0, lat + random.uniform(-scale, scale))),
        max(-180.0, min(180.0, lon + random.uniform(-scale, scale))),
    )


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def mock_user_id(index: int) -> str:
    return f"MOCK-USR-{index:06d}"


def mock_org_id(index: int) -> str:
    return f"MOCK-ORG-{index:06d}"


def mock_state_id(index: int) -> str:
    return f"ST-{index:06d}"


def mock_email(index: int, prefix: str = "volunteer") -> str:
    return f"{prefix}.{index:04d}@mock.saayam.test"


def mock_org_email(index: int) -> str:
    return f"contact.{index:04d}@mock-org.test"


def mock_phone(index: int) -> str:
    return f"+1555{index % 10000000:07d}"[:20]


def mock_person_name(index: int) -> tuple[str, str, str]:
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
    full = f"{first} {last}"
    return first, last, full


def timestamp_pair(index: int) -> tuple[str, str]:
    created = datetime(2026, 1, 1, 9, 0, 0) + timedelta(
        days=index % 200,
        hours=random.randint(0, 10),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    updated = created + timedelta(
        days=random.randint(0, 40),
        hours=random.randint(0, 8),
    )
    if updated < created:
        updated = created
    return format_ts(created), format_ts(updated)


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row.get(key) is None else row.get(key) for key in fieldnames})


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_headers(path: Path) -> List[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return next(reader)


def load_help_categories(path: Path) -> List[Dict[str, str]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            cat_id = (row.get("cat_id") or "").strip().strip('"')
            if not cat_id:
                continue
            rows.append(
                {
                    "cat_id": cat_id,
                    "cat_name": (row.get("cat_name") or "").strip().strip('"'),
                    "cat_desc": (row.get("cat_desc") or "").strip().strip('"'),
                }
            )
    if not rows:
        raise ValueError(f"No help categories loaded from {path}")
    return rows


def unique_values(rows: Iterable[Dict[str, Any]], key: str) -> List[Any]:
    return [row[key] for row in rows]
