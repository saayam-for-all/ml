"""
Mock data generator for issue #301 (Virginia analytics tables).

Generates realistic, fully synthetic .csv files for:
  countries, states, cities, users, volunteer_details, user_skills,
  volunteer_locations, user_locations, help_categories, organizations

Schema source of truth: the pluralization-renamed (states/cities/countries)
schema documented on the database repo's
"Changes to the Database, Waiting for Microservice" wiki page, plus
ddl_volunteer_locations.sql / ddl_user_locations.sql for the two location
tables (which aren't on that wiki page).

Usage:
    python generate_mock_data.py
    python generate_mock_data.py --count 400 --seed 42
    python generate_mock_data.py --output-dir ./out --count 250

No real personal data is generated: names/emails/phone numbers/addresses
are produced by Faker, and free-standing geographic reference data
(country/state/city names) uses real-world names only -- exactly like the
issue's own example ("Country: United States, State: California,
City: San Jose") -- since place names aren't personal or sensitive data.
"""

import argparse
import random
import sys

from faker import Faker

from utils import (
    format_geography_point,
    format_pg_point,
    format_timestamp,
    generate_org_id,
    generate_phone_number,
    generate_user_id,
    jitter_coordinates,
    random_created_at,
    random_dob,
    random_updated_at_after,
    write_csv,
)

# ---------------------------------------------------------------------------
# Geographic reference data
#
# Real country/state/city names + approximate centroids, exactly like the
# issue's own "Country -> State -> City" consistency example. Kept as a
# curated list (not scaled by --count) since these are lookup/reference
# tables, not fact tables -- generating e.g. 100 fake countries wouldn't be
# realistic or useful for dashboard testing.
# ---------------------------------------------------------------------------

COUNTRIES = [
    # (country_name, phone_code, country_code, is_eu_member)
    ("United States", "+1", "US", False),
    ("Canada", "+1", "CA", False),
    ("India", "+91", "IN", False),
    ("United Kingdom", "+44", "GB", True),
    ("Germany", "+49", "DE", True),
]

# state_id -> (state_name, state_code, country_name, [(city_name, lat, lon), ...])
STATES = {
    "VA": ("Virginia", "VA", "United States", [
        ("Richmond", 37.5407, -77.4360),
        ("Arlington", 38.8816, -77.0910),
        ("Norfolk", 36.8508, -76.2859),
    ]),
    "CA": ("California", "CA", "United States", [
        ("San Jose", 37.3382, -121.8863),
        ("Los Angeles", 34.0522, -118.2437),
        ("San Francisco", 37.7749, -122.4194),
    ]),
    "TX": ("Texas", "TX", "United States", [
        ("Austin", 30.2672, -97.7431),
        ("Houston", 29.7604, -95.3698),
        ("Dallas", 32.7767, -96.7970),
    ]),
    "NY": ("New York", "NY", "United States", [
        ("New York City", 40.7128, -74.0060),
        ("Buffalo", 42.8864, -78.8784),
    ]),
    "WA": ("Washington", "WA", "United States", [
        ("Seattle", 47.6062, -122.3321),
        ("Spokane", 47.6588, -117.4260),
    ]),
    "FL": ("Florida", "FL", "United States", [
        ("Miami", 25.7617, -80.1918),
        ("Orlando", 28.5383, -81.3792),
    ]),
    "IL": ("Illinois", "IL", "United States", [
        ("Chicago", 41.8781, -87.6298),
    ]),
    "MD": ("Maryland", "MD", "United States", [
        ("Baltimore", 39.2904, -76.6122),
    ]),
    "ON": ("Ontario", "ON", "Canada", [
        ("Toronto", 43.6532, -79.3832),
    ]),
    "KA": ("Karnataka", "KA", "India", [
        ("Bengaluru", 12.9716, 77.5946),
    ]),
    "EN": ("England", "EN", "United Kingdom", [
        ("London", 51.5074, -0.1278),
    ]),
    "BY": ("Bavaria", "BY", "Germany", [
        ("Munich", 48.1351, 11.5820),
    ]),
}

# Hierarchical, Saayam-style help categories (fixed reference taxonomy --
# not scaled by --count, same reasoning as the geo tables above).
HELP_CATEGORIES = [
    ("1", "FOOD", "Food assistance and distribution"),
    ("1.1", "FOOD_DISTRIBUTION", "Distributing food to those in need"),
    ("1.2", "FOOD_DONATION", "Collecting food donations"),
    ("2", "SHELTER", "Housing and shelter assistance"),
    ("2.1", "TEMPORARY_HOUSING", "Short-term housing support"),
    ("2.2", "HOME_REPAIR", "Minor home repair assistance"),
    ("3", "EDUCATION", "Educational support"),
    ("3.1", "TUTORING", "One-on-one or group tutoring"),
    ("3.2", "MENTORSHIP", "Long-term mentorship programs"),
    ("4", "HEALTHCARE", "Healthcare-related assistance"),
    ("4.1", "MEDICAL_ASSISTANCE", "Help accessing medical care"),
    ("4.2", "MENTAL_HEALTH_SUPPORT", "Mental health support services"),
    ("5", "TRANSPORTATION", "Transportation assistance"),
    ("6", "LEGAL_AID", "Legal aid and advocacy"),
    ("7", "EMPLOYMENT", "Job search and employment support"),
    ("8", "ELDERLY_CARE", "Care and companionship for the elderly"),
    ("9", "DISASTER_RELIEF", "Emergency and disaster relief"),
    ("10", "FINANCIAL_ASSISTANCE", "Short-term financial assistance"),
]

SKILL_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
ORG_TYPES = ["non_profit", "for_profit"]
ORG_SIZES = ["small", "medium", "large"]


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Generate mock data CSVs for issue #301.")
    parser.add_argument(
        "--count", type=int, default=100,
        help="Base row count for the primary entity tables (users, organizations). Default: 100.",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed, for reproducible output. Default: 42.",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="Directory to write the CSV files into. Default: current directory.",
    )
    return parser


def generate_countries():
    rows = []
    country_id_by_name = {}
    for idx, (name, phone_code, code, is_eu) in enumerate(COUNTRIES, start=1):
        country_id_by_name[name] = idx
        rows.append({
            "country_id": idx,
            "country_name": name,
            "phone_code": phone_code,
            "country_code": code,
            "last_updated_at": format_timestamp(random_created_at(days_back=400)),
            "is_eu_member": is_eu,
        })
    return rows, country_id_by_name


def generate_states(country_id_by_name):
    rows = []
    state_lookup = {}  # state_id -> (state_name, country_id, [(city_name, lat, lon)])
    for state_id, (state_name, state_code, country_name, cities) in STATES.items():
        country_id = country_id_by_name[country_name]
        state_lookup[state_id] = (state_name, country_id, cities)
        rows.append({
            "state_id": state_id,
            "country_id": country_id,
            "state_name": state_name,
            "state_code": state_code,
            "last_updated_at": format_timestamp(random_created_at(days_back=400)),
        })
    return rows, state_lookup


def generate_cities(state_lookup):
    rows = []
    city_id = 1
    # city_choices: state_id -> [(city_name, lat, lon)] for reuse when placing users/orgs
    city_choices = {}
    for state_id, (_state_name, _country_id, cities) in state_lookup.items():
        city_choices[state_id] = cities
        for city_name, lat, lon in cities:
            rows.append({
                "city_id": city_id,
                "state_id": state_id,
                "city_name": city_name,
                "lattitude": lat,
                "longitude": lon,
                "last_updated_at": format_timestamp(random_created_at(days_back=400)),
            })
            city_id += 1
    return rows, city_choices


def generate_help_categories():
    rows = []
    for cat_id, cat_name, cat_desc in HELP_CATEGORIES:
        rows.append({
            "cat_id": cat_id,
            "cat_name": cat_name,
            "cat_desc": cat_desc,
            "last_updated_at": format_timestamp(random_created_at(days_back=400)),
        })
    return rows


def generate_users(count, state_lookup, city_choices, country_id_by_name, fake, rng):
    rows = []
    # Per-user context kept in memory (not all of it is a CSV column) so
    # later tables (locations, skills, volunteer_details) can stay
    # geographically/relationally consistent with each user.
    user_context = {}
    state_ids = list(state_lookup.keys())
    country_is_eu = {cid: is_eu for (_, _, _, is_eu), cid in zip(COUNTRIES, range(1, len(COUNTRIES) + 1))}

    for i in range(1, count + 1):
        user_id = generate_user_id(i)
        state_id = rng.choice(state_ids)
        state_name, country_id, cities = state_lookup[state_id]
        city_name, city_lat, city_lon = rng.choice(cities)
        lat, lon = jitter_coordinates(city_lat, city_lon, rng=rng)

        created_at = random_created_at(rng=rng)
        updated_at = random_updated_at_after(created_at, rng=rng)

        first_name = fake.first_name()
        middle_name = fake.first_name() if rng.random() < 0.3 else None
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"

        user_context[user_id] = {
            "state_id": state_id,
            "country_id": country_id,
            "city_name": city_name,
            "lat": lat,
            "lon": lon,
        }

        rows.append({
            "user_id": user_id,
            "state_id": state_id,
            "country_id": country_id,
            "user_status_id": "",  # user_status table out of scope for #301
            "full_name": full_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "primary_email_address": fake.unique.email(),
            "primary_phone_number": generate_phone_number(rng),
            "addr_ln1": fake.street_address(),
            "addr_ln2": fake.secondary_address() if rng.random() < 0.3 else None,
            "addr_ln3": None,
            "city_name": city_name,
            "zip_code": fake.postcode(),
            "last_location": format_pg_point(lat, lon),
            "last_updated_at": format_timestamp(updated_at),
            "time_zone": fake.timezone(),
            "profile_picture_path": f"s3://saayam-mock/profile-pictures/{user_id}.jpg" if rng.random() < 0.5 else None,
            "gender": rng.choice(["Male", "Female", "Non-binary", "Prefer not to say"]),
            "language_1": "",  # supporting_languages table out of scope for #301
            "language_2": "",
            "language_3": "",
            "promotion_wizard_stage": rng.randint(0, 5),
            "promotion_wizard_last_updated_at": format_timestamp(updated_at),
            "external_auth_provider": rng.choice(["google", "facebook", "email", None, None]),
            "dob": random_dob(rng=rng).isoformat(),
            "is_eu": country_is_eu.get(country_id, False),
        })
    return rows, user_context


def generate_volunteer_details(user_context, rng, fraction=0.6):
    rows = []
    volunteer_user_ids = []
    all_user_ids = list(user_context.keys())
    sample_size = max(1, int(len(all_user_ids) * fraction))
    for user_id in rng.sample(all_user_ids, sample_size):
        volunteer_user_ids.append(user_id)
        created_at = random_created_at(rng=rng)
        updated_at = random_updated_at_after(created_at, rng=rng)
        terms_accepted = rng.random() < 0.9
        rows.append({
            "user_id": user_id,
            "terms_and_conditions": terms_accepted,
            "terms_accepted_at": format_timestamp(updated_at) if terms_accepted else None,
            "govt_id_path1": f"s3://saayam-mock/govt-ids/{user_id}_id1.pdf",
            "govt_id_path2": f"s3://saayam-mock/govt-ids/{user_id}_id2.pdf" if rng.random() < 0.5 else None,
            "path1_updated_at": format_timestamp(updated_at),
            "path2_updated_at": format_timestamp(updated_at) if rng.random() < 0.5 else None,
            "availability_days": rng.sample(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                k=rng.randint(1, 4),
            ),
            "availability_times": rng.sample(
                ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00"],
                k=rng.randint(1, 3),
            ),
            "created_at": format_timestamp(created_at),
            "last_updated_at": format_timestamp(updated_at),
        })
    return rows, volunteer_user_ids


def generate_user_skills(user_context, help_category_ids, rng, fraction=0.7):
    rows = []
    all_user_ids = list(user_context.keys())
    sample_size = max(1, int(len(all_user_ids) * fraction))
    for user_id in rng.sample(all_user_ids, sample_size):
        num_skills = rng.randint(1, 4)
        chosen_categories = rng.sample(help_category_ids, min(num_skills, len(help_category_ids)))
        for cat_id in chosen_categories:
            created_at = random_created_at(rng=rng)
            updated_at = random_updated_at_after(created_at, rng=rng)
            rows.append({
                "user_id": user_id,
                "cat_id": cat_id,
                "skill_level": rng.choice(SKILL_LEVELS),
                "created_at": format_timestamp(created_at),
                "last_updated_at": format_timestamp(updated_at),
            })
    return rows


def generate_volunteer_locations(volunteer_user_ids, user_context, rng):
    rows = []
    for user_id in volunteer_user_ids:
        ctx = user_context[user_id]
        prev_lat, prev_lon = jitter_coordinates(ctx["lat"], ctx["lon"], max_delta_degrees=0.02, rng=rng)
        curr_lat, curr_lon = jitter_coordinates(ctx["lat"], ctx["lon"], max_delta_degrees=0.02, rng=rng)
        rows.append({
            "user_id": user_id,
            "prev_loc": format_geography_point(prev_lat, prev_lon),
            "curr_loc": format_geography_point(curr_lat, curr_lon),
            "updated_at": format_timestamp(random_updated_at_after(random_created_at(days_back=60, rng=rng), rng=rng)),
        })
    return rows


def generate_user_locations(user_context, rng, fraction=0.8):
    rows = []
    all_user_ids = list(user_context.keys())
    sample_size = max(1, int(len(all_user_ids) * fraction))
    for user_id in rng.sample(all_user_ids, sample_size):
        ctx = user_context[user_id]
        prev_lat, prev_lon = jitter_coordinates(ctx["lat"], ctx["lon"], max_delta_degrees=0.02, rng=rng)
        curr_lat, curr_lon = jitter_coordinates(ctx["lat"], ctx["lon"], max_delta_degrees=0.02, rng=rng)
        rows.append({
            "user_id": user_id,
            "prev_loc": format_geography_point(prev_lat, prev_lon),
            "curr_loc": format_geography_point(curr_lat, curr_lon),
            "updated_at": format_timestamp(random_updated_at_after(random_created_at(days_back=60, rng=rng), rng=rng)),
        })
    return rows


def generate_organizations(count, state_lookup, fake, rng):
    rows = []
    for i in range(1, count + 1):
        org_id = generate_org_id(i)
        state_id = rng.choice(list(state_lookup.keys()))
        _state_name, _country_id, cities = state_lookup[state_id]
        city_name, _lat, _lon = rng.choice(cities)
        created_at = random_created_at(rng=rng)
        updated_at = random_updated_at_after(created_at, rng=rng)
        org_name = f"{fake.city()} {rng.choice(['Community Fund', 'Relief Services', 'Outreach Alliance', 'Support Network', 'Foundation', 'Volunteers Group'])}"
        rows.append({
            "org_id": org_id,
            "org_name": org_name,
            "street": fake.street_address(),
            "city_name": city_name,
            "state_id": state_id,
            "zip_code": fake.postcode(),
            "mission": fake.catch_phrase(),
            "web_url": f"https://{org_name.lower().replace(' ', '')}.org",
            "phone": generate_phone_number(rng),
            "email": fake.company_email(),
            "org_type": rng.choice(ORG_TYPES),
            "org_size": rng.choice(ORG_SIZES),
            "org_rating": rng.choice([None, 1, 2, 3, 4, 5]),
            "is_collaborator": rng.random() < 0.5,
            "created_at": format_timestamp(created_at),
            "last_updated_at": format_timestamp(updated_at),
        })
    return rows


def main():
    args = build_arg_parser().parse_args()
    rng = random.Random(args.seed)
    Faker.seed(args.seed)
    fake = Faker()

    print(f"Generating mock data (count={args.count}, seed={args.seed}) -> {args.output_dir}")

    countries, country_id_by_name = generate_countries()
    states, state_lookup = generate_states(country_id_by_name)
    cities, city_choices = generate_cities(state_lookup)
    help_categories = generate_help_categories()
    users, user_context = generate_users(args.count, state_lookup, city_choices, country_id_by_name, fake, rng)
    volunteer_details, volunteer_user_ids = generate_volunteer_details(user_context, rng)
    help_category_ids = [row["cat_id"] for row in help_categories]
    user_skills = generate_user_skills(user_context, help_category_ids, rng)
    volunteer_locations = generate_volunteer_locations(volunteer_user_ids, user_context, rng)
    user_locations = generate_user_locations(user_context, rng)
    organizations = generate_organizations(args.count, state_lookup, fake, rng)

    tables = [
        ("countries.csv", [
            "country_id", "country_name", "phone_code", "country_code",
            "last_updated_at", "is_eu_member",
        ], countries),
        ("states.csv", [
            "state_id", "country_id", "state_name", "state_code", "last_updated_at",
        ], states),
        ("cities.csv", [
            "city_id", "state_id", "city_name", "lattitude", "longitude", "last_updated_at",
        ], cities),
        ("help_categories.csv", [
            "cat_id", "cat_name", "cat_desc", "last_updated_at",
        ], help_categories),
        ("users.csv", [
            "user_id", "state_id", "country_id", "user_status_id", "full_name",
            "first_name", "middle_name", "last_name", "primary_email_address",
            "primary_phone_number", "addr_ln1", "addr_ln2", "addr_ln3", "city_name",
            "zip_code", "last_location", "last_updated_at", "time_zone",
            "profile_picture_path", "gender", "language_1", "language_2", "language_3",
            "promotion_wizard_stage", "promotion_wizard_last_updated_at",
            "external_auth_provider", "dob", "is_eu",
        ], users),
        ("volunteer_details.csv", [
            "user_id", "terms_and_conditions", "terms_accepted_at", "govt_id_path1",
            "govt_id_path2", "path1_updated_at", "path2_updated_at",
            "availability_days", "availability_times", "created_at", "last_updated_at",
        ], volunteer_details),
        ("user_skills.csv", [
            "user_id", "cat_id", "skill_level", "created_at", "last_updated_at",
        ], user_skills),
        ("volunteer_locations.csv", [
            "user_id", "prev_loc", "curr_loc", "updated_at",
        ], volunteer_locations),
        ("user_locations.csv", [
            "user_id", "prev_loc", "curr_loc", "updated_at",
        ], user_locations),
        ("organizations.csv", [
            "org_id", "org_name", "street", "city_name", "state_id", "zip_code",
            "mission", "web_url", "phone", "email", "org_type", "org_size",
            "org_rating", "is_collaborator", "created_at", "last_updated_at",
        ], organizations),
    ]

    for filename, fieldnames, rows in tables:
        path = write_csv(args.output_dir, filename, fieldnames, rows)
        print(f"  wrote {len(rows):>4} rows -> {path}")

    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
