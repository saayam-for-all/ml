import json
import os

import psycopg2
from psycopg2 import errorcodes
from psycopg2.extras import RealDictCursor


SCHEMA_NAME = os.environ.get("SAAYAM_SCHEMA", "virginia_dev_saayam_rdbms")
ORGANIZATIONS_TABLE = f"{SCHEMA_NAME}.organizations"
STATES_TABLE = f"{SCHEMA_NAME}.states"

VALID_TIME_FILTERS = {"7D", "30D", "1Y", "ALL", "CUSTOM"}
VALID_GROUP_BY = {"daily", "weekly", "monthly", "yearly"}
VALID_ORG_TYPES = {"non_profit", "for_profit"}


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body, default=str)
    }


def parse_event_body(event):
    if not event:
        return {}

    body = event.get("body")

    if body is None:
        return event

    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    if isinstance(body, dict):
        return body

    return {}


def get_db_connection():
    # Plain env vars only -- no AWS Parameter Store / SSM per issue #228 constraints.
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", 5432),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"]
    )


def normalize_org_type(value):
    if value is None:
        return "ALL"
    value = str(value).strip()
    if value.upper() == "ALL":
        return "ALL"
    return value.lower().replace("-", "_").replace(" ", "_")


def normalize_region(value):
    if value is None:
        return "ALL"
    value = str(value).strip()
    if value.upper() == "ALL":
        return "ALL"
    return value


def parse_filters(request_body):
    request_body = request_body or {}

    time_filter = str(request_body.get("time_filter") or "ALL").strip().upper()
    if time_filter not in VALID_TIME_FILTERS:
        raise ValueError(f"Invalid time_filter. Must be one of: {sorted(VALID_TIME_FILTERS)}")

    start_date = request_body.get("start_date") or None
    end_date = request_body.get("end_date") or None

    if time_filter == "CUSTOM" and (not start_date or not end_date):
        raise ValueError("start_date and end_date are required when time_filter is 'CUSTOM'")

    group_by = str(request_body.get("group_by") or "monthly").strip().lower()
    if group_by not in VALID_GROUP_BY:
        raise ValueError(f"Invalid group_by. Must be one of: {sorted(VALID_GROUP_BY)}")

    region = normalize_region(request_body.get("region", "ALL"))
    organization_type = normalize_org_type(request_body.get("organization_type", "ALL"))

    if organization_type != "ALL" and organization_type not in VALID_ORG_TYPES:
        raise ValueError(f"Invalid organization_type. Must be one of: ALL, {sorted(VALID_ORG_TYPES)}")

    return {
        "time_filter": time_filter,
        "start_date": start_date,
        "end_date": end_date,
        "group_by": group_by,
        "region": region,
        "organization_type": organization_type
    }


def build_date_filter(time_filter, start_date=None, end_date=None, column="created_at"):
    if time_filter == "CUSTOM" and start_date and end_date:
        return f"{column} BETWEEN %s AND %s", (start_date, end_date)
    if time_filter == "7D":
        return f"{column} >= CURRENT_DATE - INTERVAL '7 days'", ()
    if time_filter == "30D":
        return f"{column} >= CURRENT_DATE - INTERVAL '30 days'", ()
    if time_filter == "1Y":
        return f"{column} >= CURRENT_DATE - INTERVAL '1 year'", ()
    # ALL (or anything else) -> no date filter
    return "", ()


def get_grouping(group_by):
    mapping = {
        "daily": ("day", "YYYY-MM-DD"),
        "weekly": ("week", "YYYY-MM-DD"),
        "monthly": ("month", "YYYY-MM"),
        "yearly": ("year", "YYYY"),
    }
    if group_by not in mapping:
        raise ValueError(f"Invalid group_by. Must be one of: {sorted(VALID_GROUP_BY)}")
    return mapping[group_by]


def build_common_where(filters, alias="o"):
    """Builds the shared WHERE conditions (date range, region, organization_type)
    used across every organizations query. Returns (where_clause, params) where
    where_clause has no leading 'WHERE' -- callers prefix it themselves so the
    clause can also be combined with query-specific conditions via AND.
    """
    conditions = []
    params = []

    date_clause, date_params = build_date_filter(
        filters["time_filter"], filters["start_date"], filters["end_date"], column=f"{alias}.created_at"
    )
    if date_clause:
        conditions.append(date_clause)
        params.extend(date_params)

    if filters["region"] != "ALL":
        # Subquery (rather than a JOIN) so this helper stays self-contained and
        # never collides with a caller's own join/alias on the states table.
        conditions.append(f"{alias}.state_id IN (SELECT state_id FROM {STATES_TABLE} WHERE state_name = %s)")
        params.append(filters["region"])

    if filters["organization_type"] != "ALL":
        conditions.append(
            f"LOWER(REPLACE(REPLACE({alias}.org_type, '-', '_'), ' ', '_')) = %s"
        )
        params.append(filters["organization_type"])

    where_clause = " AND ".join(conditions)
    return where_clause, params


def is_undefined_column_error(exc):
    """True when `exc` is Postgres' 'column does not exist' error (42703) --
    used to let is_contributor degrade gracefully on DBs that lack it.
    """
    pgcode = getattr(exc, "pgcode", None)
    if pgcode == errorcodes.UNDEFINED_COLUMN:
        return True
    return "does not exist" in str(exc).lower()


if __name__ == "__main__":
    print("helpers loaded")
