# generate_mock_data.py
# Mock data for the 10 tables needed for issue #301 - local dev/testing/demos.
# No real user data anywhere here, all Faker generated.
#
# run: python generate_mock_data.py
# row counts are in the CONFIG section below

import os
import random
from datetime import datetime

import pandas as pd

from utils import (
    COUNTRIES,
    US_STATES,
    HELP_CATEGORY_TOPICS,
    SKILL_LEVELS,
    ORG_TYPES,
    ORG_SIZES,
    fake,
    generate_sid,
    generate_org_id,
    jitter_coordinates,
    created_and_updated_pair,
    pg_ts,
)

# CONFIG - change row counts here
# bumped these up to match the issue's suggested ~400 rows/file. states/countries/
# help_categories stay small on purpose - there are only 50 real US states etc,
# no point faking more of those just to hit a number
NUM_EXTRA_CITIES_PER_STATE = 7    # extra synthetic city per state on top of the real ones
NUM_USERS = 400
NUM_ORGANIZATIONS = 400
VOLUNTEER_FRACTION = 0.5          # % of users that also get a volunteer_details row
MAX_SKILLS_PER_USER = 4

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_WINDOW_START = datetime(2025, 1, 1)
DATE_WINDOW_END = datetime(2026, 8, 31, 14, 30, 0)


def write_csv(df: pd.DataFrame, name: str):
    path = os.path.join(OUTPUT_DIR, name)
    df.to_csv(path, index=False)
    print(f"  wrote {name}: {len(df)} rows")


def main():
    print("generating mock data...")

    # countries.csv
    countries_rows = []
    for i, c in enumerate(COUNTRIES, start=1):
        countries_rows.append({
            "country_id": i,
            "country_name": c["country_name"],
            "phone_code": c["phone_code"],
            "country_code": c["country_code"],
            "is_eu_member": c["is_eu_member"],
            "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
        })
    countries_df = pd.DataFrame(countries_rows)
    us_country_id = countries_df.loc[countries_df.country_code == "US", "country_id"].iloc[0]

    # states.csv - using the 2-letter code as state_id since that's what the real schema uses
    states_rows = []
    state_city_lookup = {}  # state_id -> list of (city_name, lat, lng)
    for state_name, state_code, anchor_cities in US_STATES:
        states_rows.append({
            "state_id": state_code,
            "country_id": int(us_country_id),
            "state_name": state_name,
            "state_code": state_code,
            "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
        })
        state_city_lookup[state_code] = list(anchor_cities)
    states_df = pd.DataFrame(states_rows)

    # cities.csv - wiki says hold off loading this table for real, generating it anyway since the issue asks for it
    cities_rows = []
    city_id_counter = 1
    for state_code, anchor_cities in state_city_lookup.items():
        # real anchor cities (accurate coordinates)
        for city_name, lat, lng in anchor_cities:
            cities_rows.append({
                "city_id": city_id_counter,
                "state_id": state_code,
                "city_name": city_name,
                "lattitude": lat,
                "longitude": lng,
                "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
            })
            city_id_counter += 1
        # extra synthetic cities, jittered near the state's first anchor point
        base_lat, base_lng = anchor_cities[0][1], anchor_cities[0][2]
        for _ in range(NUM_EXTRA_CITIES_PER_STATE):
            lat, lng = jitter_coordinates(base_lat, base_lng, max_delta=0.5)
            cities_rows.append({
                "city_id": city_id_counter,
                "state_id": state_code,
                "city_name": fake.city(),
                "lattitude": lat,
                "longitude": lng,
                "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
            })
            city_id_counter += 1
    cities_df = pd.DataFrame(cities_rows)

    # help_categories.csv - cat_id is hierarchical like '1', '1.1'
    help_categories_rows = []
    cat_ids = []
    for i, topic in enumerate(HELP_CATEGORY_TOPICS, start=1):
        parent_id = str(i)
        help_categories_rows.append({
            "cat_id": parent_id,
            "cat_name": topic.upper().replace(" & ", "_").replace(" ", "_"),
            "cat_desc": f"Help related to {topic.lower()}",
            "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
        })
        cat_ids.append(parent_id)
        # one child sub-category per parent for realism
        child_id = f"{i}.1"
        help_categories_rows.append({
            "cat_id": child_id,
            "cat_name": f"{topic.upper().replace(' & ', '_').replace(' ', '_')}_GENERAL",
            "cat_desc": f"General {topic.lower()} requests",
            "last_updated_at": pg_ts(fake.date_time_between_dates(DATE_WINDOW_START, DATE_WINDOW_END)),
        })
        cat_ids.append(child_id)
    help_categories_df = pd.DataFrame(help_categories_rows)

    # users.csv
    users_rows = []
    user_ids = []
    state_codes = list(state_city_lookup.keys())
    for seq in range(1, NUM_USERS + 1):
        user_id = generate_sid(seq)
        user_ids.append(user_id)
        state_id = random.choice(state_codes)
        city_choice = random.choice(state_city_lookup[state_id])
        created_at, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
        first_name = fake.first_name()
        last_name = fake.last_name()
        users_rows.append({
            "user_id": user_id,
            "state_id": state_id,
            "country_id": int(us_country_id),
            "user_status_id": None,  # user_status table out of scope for this issue
            "full_name": f"{first_name} {last_name}",
            "first_name": first_name,
            "middle_name": None,
            "last_name": last_name,
            "primary_email_address": fake.unique.email(),
            "primary_phone_number": fake.numerify("###-###-####"),
            "addr_ln1": fake.street_address(),
            "addr_ln2": None,
            "addr_ln3": None,
            "city_name": city_choice[0],
            "zip_code": fake.postcode(),
            "last_location": f"({city_choice[1]},{city_choice[2]})",
            "last_updated_at": pg_ts(updated_at),
            "time_zone": random.choice(["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]),
            "profile_picture_path": None,
            "gender": random.choice(["Male", "Female", "Non-binary", "Prefer not to say"]),
            "language_1": None,
            "language_2": None,
            "language_3": None,
            "promotion_wizard_stage": random.choice([1, 2, 3, None]),
            "promotion_wizard_last_updated_at": pg_ts(updated_at),
            "external_auth_provider": random.choice(["google", "facebook", None]),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "is_eu": False,
        })
    users_df = pd.DataFrame(users_rows)

    # organizations.csv
    org_rows = []
    org_ids = []
    for seq in range(1, NUM_ORGANIZATIONS + 1):
        org_id = generate_org_id(seq)
        org_ids.append(org_id)
        state_id = random.choice(state_codes)
        city_choice = random.choice(state_city_lookup[state_id])
        created_at, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
        org_name = f"{fake.company()} Foundation"
        org_rows.append({
            "org_id": org_id,
            "org_name": org_name,
            "street": fake.street_address(),
            "city_name": city_choice[0],
            "state_id": state_id,
            "zip_code": fake.postcode(),
            "mission": fake.sentence(nb_words=12),
            "web_url": f"https://www.{org_name.lower().replace(' ', '')}.org",
            "phone": fake.numerify("###-###-####"),
            "email": f"contact@{org_name.lower().replace(' ', '')}.org",
            "org_type": random.choice(ORG_TYPES),
            "org_size": random.choice(ORG_SIZES),
            "org_rating": random.randint(1, 5),
            "is_collaborator": random.choice([True, False]),
            "is_contributor": random.choice([True, False]),
            "created_at": pg_ts(created_at),
            "last_updated_at": pg_ts(updated_at),
        })
    organizations_df = pd.DataFrame(org_rows)

    # volunteer_details.csv - just a subset of users
    num_volunteers = int(NUM_USERS * VOLUNTEER_FRACTION)
    volunteer_user_ids = random.sample(user_ids, num_volunteers)
    volunteer_details_rows = []
    for uid in volunteer_user_ids:
        created_at, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
        volunteer_details_rows.append({
            "user_id": uid,
            "terms_and_conditions": True,
            "terms_accepted_at": pg_ts(created_at),
            "govt_id_path1": f"s3://saayam-mock/govt_ids/{uid}_1.pdf",
            "govt_id_path2": None,
            "path1_updated_at": pg_ts(created_at),
            "path2_updated_at": pg_ts(created_at),
            "availability_days": '["Monday", "Wednesday", "Saturday"]',
            "availability_times": '["Morning", "Evening"]',
            "created_at": pg_ts(created_at),
            "last_updated_at": pg_ts(updated_at),
        })
    volunteer_details_df = pd.DataFrame(volunteer_details_rows)

    # user_skills.csv - only giving volunteers skills, matches how it'd work in real usage
    user_skills_rows = []
    for uid in volunteer_user_ids:
        num_skills = random.randint(1, MAX_SKILLS_PER_USER)
        chosen_cats = random.sample(cat_ids, num_skills)
        for cat_id in chosen_cats:
            created_at, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
            user_skills_rows.append({
                "user_id": uid,
                "cat_id": cat_id,
                "skill_level": random.choice(SKILL_LEVELS),
                "created_at": pg_ts(created_at),
                "last_updated_at": pg_ts(updated_at),
            })
    user_skills_df = pd.DataFrame(user_skills_rows)

    # user_locations.csv - every user gets one
    user_locations_rows = []
    users_by_id = {u["user_id"]: u for u in users_rows}
    for uid in user_ids:
        u = users_by_id[uid]
        state_id = u["state_id"]
        anchor = random.choice(state_city_lookup[state_id])
        curr_lat, curr_lng = jitter_coordinates(anchor[1], anchor[2], max_delta=0.1)
        prev_lat, prev_lng = jitter_coordinates(anchor[1], anchor[2], max_delta=0.1)
        _, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
        user_locations_rows.append({
            "user_id": uid,
            "prev_loc": f"POINT({prev_lng} {prev_lat})",
            "curr_loc": f"POINT({curr_lng} {curr_lat})",
            "last_updated_at": pg_ts(updated_at),
        })
    user_locations_df = pd.DataFrame(user_locations_rows)

    # volunteer_locations.csv - FK is volunteer_details.user_id, NOT users.user_id (tripped me up at first)
    volunteer_locations_rows = []
    for uid in volunteer_user_ids:
        u = users_by_id[uid]
        state_id = u["state_id"]
        anchor = random.choice(state_city_lookup[state_id])
        curr_lat, curr_lng = jitter_coordinates(anchor[1], anchor[2], max_delta=0.1)
        prev_lat, prev_lng = jitter_coordinates(anchor[1], anchor[2], max_delta=0.1)
        _, updated_at = created_and_updated_pair(DATE_WINDOW_START, DATE_WINDOW_END)
        volunteer_locations_rows.append({
            "user_id": uid,
            "prev_loc": f"POINT({prev_lng} {prev_lat})",
            "curr_loc": f"POINT({curr_lng} {curr_lat})",
            "last_updated_at": pg_ts(updated_at),
        })
    volunteer_locations_df = pd.DataFrame(volunteer_locations_rows)

    print("writing csvs...")
    write_csv(countries_df, "countries.csv")
    write_csv(states_df, "states.csv")
    write_csv(cities_df, "cities.csv")
    write_csv(help_categories_df, "help_categories.csv")
    write_csv(users_df, "users.csv")
    write_csv(organizations_df, "organizations.csv")
    write_csv(volunteer_details_df, "volunteer_details.csv")
    write_csv(user_skills_df, "user_skills.csv")
    write_csv(user_locations_df, "user_locations.csv")
    write_csv(volunteer_locations_df, "volunteer_locations.csv")

    print("\nchecking for orphan FKs / dupe PKs...")
    assert states_df["country_id"].isin(countries_df["country_id"]).all(), "orphan states.country_id"
    assert cities_df["state_id"].isin(states_df["state_id"]).all(), "orphan cities.state_id"
    assert users_df["state_id"].dropna().isin(states_df["state_id"]).all(), "orphan users.state_id"
    assert users_df["country_id"].dropna().isin(countries_df["country_id"]).all(), "orphan users.country_id"
    assert organizations_df["state_id"].isin(states_df["state_id"]).all(), "orphan organizations.state_id"
    assert volunteer_details_df["user_id"].isin(users_df["user_id"]).all(), "orphan volunteer_details.user_id"
    assert user_skills_df["user_id"].isin(users_df["user_id"]).all(), "orphan user_skills.user_id"
    assert user_skills_df["cat_id"].isin(help_categories_df["cat_id"]).all(), "orphan user_skills.cat_id"
    assert user_locations_df["user_id"].isin(users_df["user_id"]).all(), "orphan user_locations.user_id"
    assert volunteer_locations_df["user_id"].isin(volunteer_details_df["user_id"]).all(), "orphan volunteer_locations.user_id"
    assert users_df["user_id"].is_unique, "duplicate users.user_id"
    assert organizations_df["org_id"].is_unique, "duplicate organizations.org_id"
    assert help_categories_df["cat_id"].is_unique, "duplicate help_categories.cat_id"
    print("all checks passed")


if __name__ == "__main__":
    main()
