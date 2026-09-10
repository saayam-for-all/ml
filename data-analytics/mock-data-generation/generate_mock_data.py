"""Generate synthetic Virginia analytics CSVs for dashboard and API testing.

Issue: https://github.com/saayam-for-all/data/issues/301

Filenames use the 8/17/2026 pluralization (countries, states, cities).
Personally identifiable values are invented; they are not copied from live users.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

from utils import (
    DEFAULT_ROWS,
    DEFAULT_SEED,
    EXAMPLE_TS,
    GENDERS,
    GEO_SEEDS,
    LANGUAGES,
    MISSIONS,
    ORG_PREFIXES,
    ORG_SIZES,
    ORG_SOURCES,
    ORG_SUFFIXES,
    ORG_TYPES,
    TIMEZONES,
    ewkt_point,
    format_date,
    format_ts,
    haversine_km,
    jitter_coord,
    json_text,
    load_help_categories,
    mock_email,
    mock_org_email,
    mock_org_id,
    mock_person_name,
    mock_phone,
    mock_state_id,
    mock_user_id,
    parse_ewkt_point,
    parse_ts,
    read_csv,
    set_seed,
    timestamp_pair,
    write_csv,
)

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
HELP_CATEGORIES_LOOKUP = (
    REPO_ROOT / "database" / "lookup_tables" / "help_categories.csv"
)

COUNTRIES_FIELDS = [
    "country_id",
    "country_name",
    "phone_code",
    "country_code",
    "last_update_date",
    "is_eu_member",
]
STATES_FIELDS = [
    "state_id",
    "country_id",
    "state_name",
    "state_code",
    "last_update_date",
]
CITIES_FIELDS = [
    "city_id",
    "state_id",
    "city_name",
    "lattitude",
    "longitude",
    "last_update_date",
]
USERS_FIELDS = [
    "user_id",
    "state_id",
    "country_id",
    "user_status_id",
    "user_category_id",
    "full_name",
    "first_name",
    "middle_name",
    "last_name",
    "primary_email_address",
    "primary_phone_number",
    "addr_ln1",
    "addr_ln2",
    "addr_ln3",
    "city_name",
    "zip_code",
    "last_location",
    "last_update_date",
    "time_zone",
    "profile_picture_path",
    "gender",
    "language_1",
    "language_2",
    "language_3",
    "promotion_wizard_stage",
    "promotion_wizard_last_update_date",
    "external_auth_provider",
    "dob",
]
VOLUNTEER_DETAILS_FIELDS = [
    "user_id",
    "terms_and_conditions",
    "terms_accepted_at",
    "govt_id_path1",
    "govt_id_path2",
    "path1_updated_at",
    "path2_updated_at",
    "availability_days",
    "availability_times",
    "created_at",
    "last_updated_at",
]
USER_SKILLS_FIELDS = ["user_id", "cat_id", "created_date", "last_update_date"]
LOCATION_FIELDS = ["user_id", "prev_loc", "curr_loc", "updated_at"]
HELP_CATEGORIES_FIELDS = ["cat_id", "cat_name", "cat_desc"]
ORGANIZATIONS_FIELDS = [
    "org_id",
    "org_name",
    "org_type",
    "street",
    "city_name",
    "state_id",
    "state_code",
    "zip_code",
    "mission",
    "web_url",
    "phone",
    "email",
    "org_size",
    "org_rating",
    "is_collaborator",
    "is_contributor",
    "source",
    "cat_id",
    "created_at",
    "last_updated_at",
]

TABLE_FILES = {
    "countries": ("countries.csv", COUNTRIES_FIELDS),
    "states": ("states.csv", STATES_FIELDS),
    "cities": ("cities.csv", CITIES_FIELDS),
    "help_categories": ("help_categories.csv", HELP_CATEGORIES_FIELDS),
    "users": ("users.csv", USERS_FIELDS),
    "volunteer_details": ("volunteer_details.csv", VOLUNTEER_DETAILS_FIELDS),
    "user_skills": ("user_skills.csv", USER_SKILLS_FIELDS),
    "volunteer_locations": ("volunteer_locations.csv", LOCATION_FIELDS),
    "user_locations": ("user_locations.csv", LOCATION_FIELDS),
    "organizations": ("organizations.csv", ORGANIZATIONS_FIELDS),
}


def _seed_for(index: int) -> Dict[str, Any]:
    return GEO_SEEDS[index % len(GEO_SEEDS)]


def generate_countries(n: int) -> List[Dict[str, Any]]:
    unique_seeds = []
    seen_codes = set()
    for seed in GEO_SEEDS:
        if seed["country_code"] in seen_codes:
            continue
        seen_codes.add(seed["country_code"])
        unique_seeds.append(seed)

    rows = []
    for i, seed in enumerate(unique_seeds, start=1):
        if i > n:
            break
        rows.append(
            {
                "country_id": i,
                "country_name": seed["country_name"],
                "phone_code": str(seed["phone_code"])[:5],
                "country_code": seed["country_code"][:6],
                "last_update_date": EXAMPLE_TS,
                "is_eu_member": seed["is_eu_member"],
            }
        )
    next_id = len(rows) + 1
    while len(rows) < n:
        rows.append(
            {
                "country_id": next_id,
                "country_name": f"MOCK_COUNTRY_{next_id:03d}",
                "phone_code": str(100 + (next_id % 800))[:5],
                "country_code": f"M{next_id:03d}"[:6],
                "last_update_date": EXAMPLE_TS,
                "is_eu_member": next_id % 9 == 0,
            }
        )
        next_id += 1
    return rows


def generate_states(n: int, countries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for i in range(1, n + 1):
        seed = _seed_for(i - 1)
        country = countries[(i - 1) % len(countries)]
        if i <= len(GEO_SEEDS):
            name = seed["state_name"]
            code = seed["state_code"]
            country_id = country["country_id"]
            # Keep seeded states on the matching seeded country when possible.
            for candidate in countries:
                if candidate["country_name"] == seed["country_name"]:
                    country_id = candidate["country_id"]
                    break
        else:
            name = f"MOCK_STATE_{i:03d}"
            code = f"S{i:03d}"[:6]
            country_id = country["country_id"]
        rows.append(
            {
                "state_id": mock_state_id(i),
                "country_id": country_id,
                "state_name": name,
                "state_code": code,
                "last_update_date": EXAMPLE_TS,
            }
        )
    return rows


def generate_cities(n: int, states: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for i in range(1, n + 1):
        seed = _seed_for(i - 1)
        state = states[i - 1]
        if i <= len(GEO_SEEDS):
            name = seed["city_name"][:30]
            lat, lon = seed["lat"], seed["lon"]
        else:
            name = f"Mock City {i:03d}"[:30]
            lat, lon = jitter_coord(seed["lat"], seed["lon"], scale=1.5)
        rows.append(
            {
                "city_id": i,
                "state_id": state["state_id"],
                "city_name": name,
                "lattitude": round(lat, 6),
                "longitude": round(lon, 6),
                "last_update_date": EXAMPLE_TS,
            }
        )
    return rows


def generate_users(
    n: int,
    cities: Sequence[Dict[str, Any]],
    states: Sequence[Dict[str, Any]],
    countries: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    state_by_id = {row["state_id"]: row for row in states}
    country_by_id = {row["country_id"]: row for row in countries}
    rows = []
    for i in range(1, n + 1):
        city = cities[i - 1]
        state = state_by_id[city["state_id"]]
        country = country_by_id[state["country_id"]]
        seed = _seed_for(i - 1)
        first, last, full = mock_person_name(i)
        created, updated = timestamp_pair(i)
        lat, lon = jitter_coord(float(city["lattitude"]), float(city["longitude"]), 0.04)
        rows.append(
            {
                "user_id": mock_user_id(i),
                "state_id": state["state_id"],
                "country_id": country["country_id"],
                "user_status_id": 1,
                "user_category_id": 2,
                "full_name": full,
                "first_name": first,
                "middle_name": "",
                "last_name": last,
                "primary_email_address": mock_email(i),
                "primary_phone_number": mock_phone(i),
                "addr_ln1": f"{100 + i} Mock Street",
                "addr_ln2": "",
                "addr_ln3": "",
                "city_name": city["city_name"],
                "zip_code": seed["zip_code"] if i <= len(GEO_SEEDS) else f"{10000 + i % 89999}",
                "last_location": ewkt_point(lon, lat),
                "last_update_date": updated,
                "time_zone": seed.get("time_zone") or TIMEZONES[i % len(TIMEZONES)],
                "profile_picture_path": "",
                "gender": GENDERS[i % len(GENDERS)],
                "language_1": LANGUAGES[i % len(LANGUAGES)],
                "language_2": LANGUAGES[(i + 1) % len(LANGUAGES)],
                "language_3": "",
                "promotion_wizard_stage": "",
                "promotion_wizard_last_update_date": "",
                "external_auth_provider": "",
                "dob": format_date(
                    parse_ts(created).replace(year=1980 + (i % 25), month=1 + (i % 12), day=1 + (i % 27))
                ),
            }
        )
    return rows


def generate_volunteer_details(users: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for i, user in enumerate(users, start=1):
        created, updated = timestamp_pair(i + 17)
        accepted = created
        rows.append(
            {
                "user_id": user["user_id"],
                "terms_and_conditions": True,
                "terms_accepted_at": accepted,
                "govt_id_path1": f"uploads/mock/id-front-{i:04d}.jpg",
                "govt_id_path2": f"uploads/mock/id-back-{i:04d}.jpg",
                "path1_updated_at": updated,
                "path2_updated_at": updated,
                "availability_days": json_text(
                    {"monday": True, "wednesday": True, "saturday": i % 2 == 0}
                ),
                "availability_times": json_text({"morning": True, "evening": i % 3 == 0}),
                "created_at": created,
                "last_updated_at": updated,
            }
        )
    return rows


def generate_user_skills(
    n: int,
    users: Sequence[Dict[str, Any]],
    help_categories: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    usable = [row for row in help_categories if row["cat_id"] != "0.0.0.0.0"] or list(
        help_categories
    )
    rows = []
    seen = set()
    i = 0
    max_pairs = len(users) * len(usable)
    target = min(n, max_pairs)
    while len(rows) < target:
        user = users[i % len(users)]
        cat = usable[(i // len(users)) % len(usable)] if i >= len(users) else usable[i % len(usable)]
        key = (user["user_id"], cat["cat_id"])
        i += 1
        if key in seen:
            continue
        seen.add(key)
        created, updated = timestamp_pair(len(rows) + 3)
        rows.append(
            {
                "user_id": user["user_id"],
                "cat_id": cat["cat_id"],
                "created_date": created,
                "last_update_date": updated,
            }
        )
        if i > max_pairs * 3:
            break
    return rows


def generate_locations(
    users: Sequence[Dict[str, Any]],
    cities: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    city_by_name_state = {
        (row["city_name"], row["state_id"]): row for row in cities
    }
    rows = []
    for i, user in enumerate(users, start=1):
        city = city_by_name_state[(user["city_name"], user["state_id"])]
        curr_lat, curr_lon = jitter_coord(
            float(city["lattitude"]), float(city["longitude"]), 0.03
        )
        prev_lat, prev_lon = jitter_coord(curr_lat, curr_lon, 0.02)
        _, updated = timestamp_pair(i + 9)
        rows.append(
            {
                "user_id": user["user_id"],
                "prev_loc": ewkt_point(prev_lon, prev_lat),
                "curr_loc": ewkt_point(curr_lon, curr_lat),
                "updated_at": updated,
            }
        )
    return rows


def generate_organizations(
    n: int,
    states: Sequence[Dict[str, Any]],
    cities: Sequence[Dict[str, Any]],
    help_categories: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    city_by_state = {}
    for city in cities:
        city_by_state.setdefault(city["state_id"], city)
    usable = [row for row in help_categories if row["cat_id"] != "0.0.0.0.0"] or list(
        help_categories
    )
    rows = []
    for i in range(1, n + 1):
        state = states[i - 1]
        city = city_by_state[state["state_id"]]
        created, updated = timestamp_pair(i + 40)
        prefix = ORG_PREFIXES[i % len(ORG_PREFIXES)]
        suffix = ORG_SUFFIXES[i % len(ORG_SUFFIXES)]
        rows.append(
            {
                "org_id": mock_org_id(i),
                "org_name": f"{prefix} {suffix} {i:03d}"[:125],
                "org_type": ORG_TYPES[i % len(ORG_TYPES)],
                "street": f"{200 + i} Mock Avenue",
                "city_name": city["city_name"],
                "state_id": state["state_id"],
                "state_code": state["state_code"],
                "zip_code": f"{20000 + i % 70000}"[:10],
                "mission": MISSIONS[i % len(MISSIONS)],
                "web_url": f"https://mock-org-{i:04d}.example.test",
                "phone": mock_phone(i + 5000),
                "email": mock_org_email(i),
                "org_size": ORG_SIZES[i % len(ORG_SIZES)],
                "org_rating": 1 + (i % 5),
                "is_collaborator": i % 2 == 0,
                "is_contributor": i % 3 == 0,
                "source": ORG_SOURCES[i % len(ORG_SOURCES)],
                "cat_id": usable[i % len(usable)]["cat_id"],
                "created_at": created,
                "last_updated_at": updated,
            }
        )
    return rows


def generate_all(
    n: int,
    seed: int = DEFAULT_SEED,
    help_categories_path: Path = HELP_CATEGORIES_LOOKUP,
) -> Dict[str, List[Dict[str, Any]]]:
    set_seed(seed)
    help_categories = load_help_categories(help_categories_path)
    countries = generate_countries(n)
    states = generate_states(n, countries)
    cities = generate_cities(n, states)
    users = generate_users(n, cities, states, countries)
    volunteer_details = generate_volunteer_details(users)
    return {
        "countries": countries,
        "states": states,
        "cities": cities,
        "help_categories": help_categories,
        "users": users,
        "volunteer_details": volunteer_details,
        "user_skills": generate_user_skills(n, users, help_categories),
        "volunteer_locations": generate_locations(users, cities),
        "user_locations": generate_locations(users, cities),
        "organizations": generate_organizations(n, states, cities, help_categories),
    }


def _ids(rows: Sequence[Dict[str, Any]], key: str) -> set:
    return {str(row[key]) for row in rows}


def _require(condition: bool, message: str, errors: List[str]) -> None:
    if not condition:
        errors.append(message)


def validate_dataset(data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    errors: List[str] = []
    countries = data["countries"]
    states = data["states"]
    cities = data["cities"]
    users = data["users"]
    volunteers = data["volunteer_details"]
    skills = data["user_skills"]
    vol_locs = data["volunteer_locations"]
    user_locs = data["user_locations"]
    orgs = data["organizations"]
    categories = data["help_categories"]

    def unique(rows, key, label):
        values = [str(row[key]) for row in rows]
        _require(len(values) == len(set(values)), f"{label}: duplicate {key}", errors)

    unique(countries, "country_id", "countries")
    unique(states, "state_id", "states")
    unique(cities, "city_id", "cities")
    unique(users, "user_id", "users")
    unique(volunteers, "user_id", "volunteer_details")
    unique(vol_locs, "user_id", "volunteer_locations")
    unique(user_locs, "user_id", "user_locations")
    unique(orgs, "org_id", "organizations")
    unique(categories, "cat_id", "help_categories")
    skill_keys = [(row["user_id"], row["cat_id"]) for row in skills]
    _require(len(skill_keys) == len(set(skill_keys)), "user_skills: duplicate PK", errors)

    country_ids = _ids(countries, "country_id")
    state_ids = _ids(states, "state_id")
    user_ids = _ids(users, "user_id")
    volunteer_ids = _ids(volunteers, "user_id")
    cat_ids = _ids(categories, "cat_id")
    city_lookup = {(row["city_name"], row["state_id"]): row for row in cities}
    state_by_id = {str(row["state_id"]): row for row in states}

    for row in states:
        _require(
            str(row["country_id"]) in country_ids,
            f"states orphan country_id={row['country_id']}",
            errors,
        )
        _require(row.get("country_id") not in ("", None), "states.country_id is required", errors)

    for row in cities:
        _require(str(row["state_id"]) in state_ids, f"cities orphan state_id={row['state_id']}", errors)

    for row in users:
        _require(str(row["state_id"]) in state_ids, f"users orphan state_id={row['state_id']}", errors)
        _require(
            str(row["country_id"]) in country_ids,
            f"users orphan country_id={row['country_id']}",
            errors,
        )
        state = state_by_id[str(row["state_id"])]
        _require(
            str(state["country_id"]) == str(row["country_id"]),
            f"users {row['user_id']} country/state mismatch",
            errors,
        )
        _require(
            (row["city_name"], row["state_id"]) in city_lookup,
            f"users {row['user_id']} city/state mismatch",
            errors,
        )
        _require(
            str(row["primary_email_address"]).endswith(".test"),
            f"users {row['user_id']} email is not a mock .test address",
            errors,
        )
        _require("555" in str(row["primary_phone_number"]), "phone must use 555 mock prefix", errors)

    for row in volunteers:
        _require(row["user_id"] in user_ids, f"volunteer_details orphan user_id={row['user_id']}", errors)
        _require(
            parse_ts(row["created_at"]) <= parse_ts(row["last_updated_at"]),
            f"volunteer_details timestamp order {row['user_id']}",
            errors,
        )

    for row in skills:
        _require(row["user_id"] in user_ids, f"user_skills orphan user_id={row['user_id']}", errors)
        _require(row["cat_id"] in cat_ids, f"user_skills orphan cat_id={row['cat_id']}", errors)
        _require(
            parse_ts(row["created_date"]) <= parse_ts(row["last_update_date"]),
            f"user_skills timestamp order {row['user_id']}",
            errors,
        )

    for row in vol_locs:
        _require(
            row["user_id"] in volunteer_ids,
            f"volunteer_locations must reference volunteer_details: {row['user_id']}",
            errors,
        )
    for row in user_locs:
        _require(row["user_id"] in user_ids, f"user_locations orphan user_id={row['user_id']}", errors)

    user_by_id = {row["user_id"]: row for row in users}
    for row in vol_locs + user_locs:
        user = user_by_id[row["user_id"]]
        city = city_lookup[(user["city_name"], user["state_id"])]
        lon, lat = parse_ewkt_point(row["curr_loc"])
        distance = haversine_km(lat, lon, float(city["lattitude"]), float(city["longitude"]))
        _require(distance < 250, f"location too far from city for {row['user_id']}: {distance:.1f}km", errors)
        parse_ewkt_point(row["prev_loc"])

    for row in orgs:
        _require(str(row["state_id"]) in state_ids, f"organizations orphan state_id={row['state_id']}", errors)
        _require(row["cat_id"] in cat_ids, f"organizations orphan cat_id={row['cat_id']}", errors)
        _require(
            (row["city_name"], row["state_id"]) in city_lookup,
            f"organizations city/state mismatch {row['org_id']}",
            errors,
        )
        _require(
            parse_ts(row["created_at"]) <= parse_ts(row["last_updated_at"]),
            f"organizations timestamp order {row['org_id']}",
            errors,
        )
        _require(str(row["email"]).endswith(".test"), f"org email not mock: {row['email']}", errors)

    return errors


def write_dataset(data: Dict[str, List[Dict[str, Any]]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, (filename, fields) in TABLE_FILES.items():
        write_csv(output_dir / filename, data[key], fields)


def load_dataset(output_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    loaded = {}
    for key, (filename, _fields) in TABLE_FILES.items():
        loaded[key] = read_csv(output_dir / filename)
    return loaded


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate #301 mock CSVs")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="Rows per generated table (default 400)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument(
        "--help-categories",
        type=Path,
        default=HELP_CATEGORIES_LOOKUP,
        help="Lookup CSV used for official help_categories rows",
    )
    parser.add_argument("--validate-only", action="store_true", help="Validate existing CSVs and exit")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.rows < 1:
        print("--rows must be >= 1", file=sys.stderr)
        return 2
    output_dir = args.output_dir.resolve()
    if args.validate_only:
        data = load_dataset(output_dir)
    else:
        data = generate_all(args.rows, seed=args.seed, help_categories_path=args.help_categories)
        write_dataset(data, output_dir)
    errors = validate_dataset(data)
    if errors:
        print(f"Validation failed ({len(errors)} issues):", file=sys.stderr)
        for error in errors[:40]:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Wrote/validated mock data in {output_dir}")
    for key, (filename, _fields) in TABLE_FILES.items():
        print(f"  {filename}: {len(data[key])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
