# Mock data for Virginia analytics tables

Synthetic CSV data for local development, API testing, dashboard testing, and demos.

**Issue:** [#301](https://github.com/saayam-for-all/data/issues/301)

Do not use these files as production data. Names, emails, phones, and IDs are invented (`MOCK-USR-*`, `@mock.saayam.test`, `+1555…`).

## Tables

| CSV file | Schema table (8/17/2026 pluralization) |
|---|---|
| `countries.csv` | `countries` |
| `states.csv` | `states` |
| `cities.csv` | `cities` |
| `users.csv` | `users` |
| `volunteer_details.csv` | `volunteer_details` |
| `user_skills.csv` | `user_skills` |
| `volunteer_locations.csv` | `volunteer_locations` |
| `user_locations.csv` | `user_locations` |
| `help_categories.csv` | `help_categories` |
| `organizations.csv` | `organizations` |

`help_categories.csv` is copied from the official lookup (`database/lookup_tables/help_categories.csv`) so `cat_id` values stay aligned with the live category tree. That table is bounded by unique category IDs (about 80 rows), not the `--rows` count.

Column names follow the current Virginia DDL in `saayam-for-all/database` (`ddl/Tables/`). `organizations.csv` uses `state_id`, `org_size`, `org_rating`, and `is_collaborator`. `org_type` is `non_profit`/`for_profit` and `org_size` is `small`/`medium`/`large`. `users.last_location` is a native PostgreSQL point `(lon,lat)`, not PostGIS EWKT. `user_skills` timestamps are `created_at`/`last_updated_at`.

## Python dependencies

Python 3.10+ and the standard library only (`csv`, `json`, `argparse`, `unittest`). No extra packages.

## How to generate

From this directory:

```bash
python generate_mock_data.py
```

Defaults: **400** rows per generated table, seed **42**, output written here.

```bash
python generate_mock_data.py --rows 400 --seed 42 --output-dir .
```

```bash
python generate_mock_data.py --rows 100 --output-dir /tmp/saayam-mock
```

## Row counts

`--rows` controls countries, states, cities, users, volunteer_details, user_skills, volunteer_locations, user_locations, and organizations.

The generator is reusable: raise `--rows` later without changing the core logic.

## Relationships

```text
countries.country_id
    ↑
states.country_id          states.state_id
    ↑                           ↑
users.country_id           users.state_id
                           cities.state_id
                           organizations.state_id

users.user_id
    ↑
volunteer_details.user_id
    ↑
volunteer_locations.user_id     (not users.user_id directly)

users.user_id
    ↑
user_locations.user_id
user_skills.user_id

help_categories.cat_id
    ↑
user_skills.cat_id
```

Geographic chain: country → state → city → ZIP / `curr_loc` / `prev_loc`. Location-table points are EWKT (`SRID=4326;POINT(lon lat)`) near the user’s city centroid. `users.last_location` uses PostgreSQL point `(lon,lat)`.

Each generated row after the six public seed cities gets its own mock country/state/city/ZIP/timezone instead of inheriting an unrelated real centroid.

`states.country_id` is always populated (schema `NOT NULL`).

## Output location

`data-analytics/mock-data-generation/`

## Validation

The generator validates after writing:

- unique primary keys
- CSV headers match the table column contract (name and order)
- foreign keys (no orphans)
- `created_*` ≤ `last_updated_*` / `last_update_date`
- mock emails/phones
- volunteer locations only for `volunteer_details` users
- `curr_loc` and `prev_loc` both near the assigned city

```bash
python generate_mock_data.py --validate-only
python -m unittest test_generate_mock_data.py
```

Run tests from this directory so `generate_mock_data` imports.
