from datetime import datetime

import pytest
from flask import Flask

import src.organization_analytics as organization_module
from src.organization_analytics import (
    build_analytics,
    build_organization_query,
    default_response,
    fetch_organization_rows,
    organization_analytics,
    parse_filters,
)


def organization_row(**overrides):
    row = {
        "org_id": "ORG1",
        "city_name": "Austin",
        "state_id": "TX",
        "state_name": "Texas",
        "org_size": "Small",
        "org_rating": 5,
        "is_collaborator": True,
        "is_contributor": False,
        "org_type": "Non-Profit",
        "created_at": datetime(2026, 1, 15),
    }
    row.update(overrides)
    return row


class Cursor:
    def __init__(self, rows=None, first_error=None):
        self.rows = rows or []
        self.first_error = first_error
        self.calls = []

    def execute(self, query, params=()):
        self.calls.append((query, params))
        if self.first_error and len(self.calls) == 1:
            raise self.first_error

    def fetchall(self):
        return self.rows

    def close(self):
        pass


def test_filters_and_parameterized_custom_dates():
    filters = parse_filters({"time_filter": "CUSTOM", "start_date": "2026-01-01", "end_date": "2026-06-30", "group_by": "monthly", "region": "California", "organization_type": "non_profit"})
    query, params = build_organization_query(filters)
    assert "%s" in query
    assert params == ("2026-01-01", "2026-06-30", "California", "California", "California", "non_profit")


@pytest.mark.parametrize("payload", [{"time_filter": "BAD"}, {"time_filter": "CUSTOM", "start_date": "2026-01-01"}, {"group_by": "hourly"}, {"organization_type": "charity"}])
def test_invalid_filters_are_rejected(payload):
    with pytest.raises(ValueError):
        parse_filters(payload)


def test_empty_result_has_complete_response_shape():
    assert build_analytics([]) == default_response()


def test_metrics_and_null_rating_are_safe():
    rows = [organization_row(), organization_row(org_id="ORG2", org_rating=None, is_collaborator=False, is_contributor=True, org_type="For-profit", created_at=datetime(2026, 2, 2))]
    response = build_analytics(rows)
    assert response["summary"] == {"total_organizations": 2, "total_collaborators": 1, "total_contributors": 1, "average_org_rating": 5.0}
    assert response["rating_distribution"] == [{"rating": 1, "organization_count": 0}, {"rating": 2, "organization_count": 0}, {"rating": 3, "organization_count": 0}, {"rating": 4, "organization_count": 0}, {"rating": 5, "organization_count": 1}]
    assert response["organization_type_distribution"][0]["total"] == 1


def test_missing_is_contributor_column_uses_compatibility_query():
    cursor = Cursor(rows=[organization_row(is_contributor=False)], first_error=RuntimeError("column is_contributor does not exist"))
    rows = fetch_organization_rows(cursor, parse_filters({}))
    assert len(cursor.calls) == 2
    assert "FALSE AS is_contributor" in cursor.calls[1][0]
    assert rows[0]["org_id"] == "ORG1"


def test_database_error_is_not_hidden_from_query_helper():
    cursor = Cursor(first_error=RuntimeError("database unavailable"))
    with pytest.raises(RuntimeError, match="database unavailable"):
        fetch_organization_rows(cursor, parse_filters({}))


def test_post_endpoint_returns_dashboard_response(monkeypatch):
    class Connection:
        def __init__(self):
            self.cursor_instance = Cursor(rows=[organization_row()])

        def cursor(self):
            return self.cursor_instance

        def close(self):
            pass

    monkeypatch.setattr(organization_module, "get_db_connection", lambda: Connection())
    app = Flask(__name__)
    app.register_blueprint(organization_analytics)

    response = app.test_client().post("/analytics/organizations", json={"time_filter": "ALL", "group_by": "monthly"})

    assert response.status_code == 200
    assert set(response.json) == set(default_response())
    assert response.json["summary"]["total_organizations"] == 1