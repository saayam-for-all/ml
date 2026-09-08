"""
Shared helpers for the issue #301 mock-data generator.

Kept separate from generate_mock_data.py so the ID/geo/date logic can be
reused or unit-tested independently of the table-by-table generation flow.
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# ID generators (mirror the format the real DB triggers produce)
# ---------------------------------------------------------------------------

def generate_user_id(seq_id):
    """
    Mirrors virginia_dev_saayam_rdbms.generate_sid(): a 15-digit sequence
    zero-padded and split into 5 groups of 3, prefixed 'SID-00-'.
    """
    padded = str(seq_id).zfill(15)
    groups = [padded[i:i + 3] for i in range(0, 15, 3)]
    return "SID-00-" + "-".join(groups)


def generate_phone_number(rng=random):
    """
    A fixed-format '+1-XXX-XXX-XXXX' phone number (15 chars).

    Faker's default phone_number() provider occasionally produces strings
    longer than organizations.phone's VARCHAR(20) limit (extensions like
    'x1234' push it over) -- this format is short and consistent enough to
    safely fit every phone column in the schema.
    """
    return "+1-{:03d}-{:03d}-{:04d}".format(
        rng.randint(200, 999), rng.randint(200, 999), rng.randint(0, 9999)
    )


def generate_org_id(seq_id):
    """
    Mirrors virginia_dev_saayam_rdbms.generate_org_id(): a sequence split
    into 3 groups of 3 digits, prefixed 'ORG-00-'.
    """
    padded = str(seq_id).zfill(9)
    groups = [padded[i:i + 3] for i in range(0, 9, 3)]
    return "ORG-00-" + "-".join(groups)


# ---------------------------------------------------------------------------
# Geographic helpers
# ---------------------------------------------------------------------------

def jitter_coordinates(lat, lon, max_delta_degrees=0.05, rng=random):
    """
    Nudges a city's centroid by a small random offset (~<= ~5km at these
    latitudes) so multiple records "near" the same city aren't all stacked
    on the exact same point, while staying plausibly within that city.
    """
    return (
        round(lat + rng.uniform(-max_delta_degrees, max_delta_degrees), 6),
        round(lon + rng.uniform(-max_delta_degrees, max_delta_degrees), 6),
    )


def format_pg_point(lat, lon):
    """
    Format for the `users.last_location` column (Postgres `point` type).
    The DDL's own example comment writes it as '(lat, lng)', e.g.
    '(37.3382, -121.8863)' for San Jose -- matched here for consistency.
    """
    return f"({lat}, {lon})"


def format_geography_point(lat, lon):
    """
    Format for `geography(Point, 4326)` columns (volunteer_locations /
    user_locations' curr_loc / prev_loc). PostGIS WKT text is 'POINT(lon lat)'
    -- longitude first -- which is what ST_GeogFromText()/COPY expect.
    """
    return f"POINT({lon} {lat})"


# ---------------------------------------------------------------------------
# Date/time helpers
# ---------------------------------------------------------------------------

PG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_timestamp(dt):
    return dt.strftime(PG_TIMESTAMP_FORMAT)


def random_created_at(days_back=730, rng=random):
    """A random timestamp within the last `days_back` days (default ~2 years)."""
    now = datetime.now(timezone.utc)
    delta_seconds = rng.randint(0, days_back * 24 * 3600)
    return now - timedelta(seconds=delta_seconds)


def random_updated_at_after(created_at, rng=random):
    """
    A timestamp >= created_at and <= now, so created_at <= last_updated_at
    always holds for tables that track both.
    """
    now = datetime.now(timezone.utc)
    if created_at >= now:
        return created_at
    max_gap = int((now - created_at).total_seconds())
    return created_at + timedelta(seconds=rng.randint(0, max_gap))


def random_dob(min_age=18, max_age=75, rng=random):
    today = datetime.now(timezone.utc).date()
    age_days = rng.randint(min_age * 365, max_age * 365)
    return today - timedelta(days=age_days)


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def write_csv(output_dir, filename, fieldnames, rows):
    """Writes `rows` (list of dicts) to `output_dir/filename` with a fixed
    column order, JSON-encoding any dict/list field values along the way."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            serialized = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                serialized[key] = "" if value is None else value
            writer.writerow(serialized)
    return path
