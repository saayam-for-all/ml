# Mock Data Generation (Issue #301)

Generates realistic, fully synthetic `.csv` mock data for the Virginia
analytics tables, for local development, API testing, dashboard testing,
and demonstrations. No real or sensitive user information is used.

## Purpose

Provides reproducible seed data for the 10 tables below so dashboards and
APIs (e.g. the KPI, volunteer, beneficiary, and organization analytics
Lambdas) can be developed and tested locally without access to production
data or AWS.

## Tables included

| Table | Description |
|---|---|
| `countries.csv` | Country reference data |
| `states.csv` | State reference data (per country) |
| `cities.csv` | City reference data (per state), with centroid lat/lon |
| `help_categories.csv` | Hierarchical help-category taxonomy |
| `users.csv` | User profiles |
| `volunteer_details.csv` | Volunteer-specific profile data (subset of users) |
| `user_skills.csv` | User &lt;-&gt; help-category skill mappings |
| `volunteer_locations.csv` | Current/previous geo-location for volunteers |
| `user_locations.csv` | Current/previous geo-location for users |
| `organizations.csv` | Organization profiles |

## Schema source

Column names, types, and foreign keys are taken from the current
(post-pluralization-rename) Virginia schema documented on the
[database repo's "Changes to the Database, Waiting for Microservice" wiki
page](https://github.com/saayam-for-all/database/wiki/*-Changes-to-the-Database,-Waiting-for-Microservice),
plus `ddl_volunteer_locations.sql` / `ddl_user_locations.sql` (not on that
wiki page). Table names `states`, `cities`, and `countries` use the
pluralized names per the 8/17/2026 rename noted in issue #301 -- the
per-table DDL blocks on the wiki still show the older singular names.

## Requirements

- Python 3.9+
- [`Faker`](https://pypi.org/project/Faker/):
  ```bash
  pip install Faker
  ```

## How to run

```bash
cd data-analytics/mock-data-generation
python generate_mock_data.py
```

This writes all 10 CSVs into the current directory using the defaults
(100 base rows, seed 42).

## Configuring row counts

```bash
python generate_mock_data.py --count 400 --seed 7 --output-dir ./out
```

- `--count` sets the row count for the two primary entity tables (`users`,
  `organizations`); it defaults to 100. Every table that has a foreign key
  into `users` or `organizations` (`volunteer_details`, `user_skills`,
  `volunteer_locations`, `user_locations`) scales proportionally and
  automatically -- no code changes needed to generate a larger dataset.
- `--seed` controls the random seed, for reproducible output between runs.
- `--output-dir` controls where the CSVs are written.
- `countries.csv`, `states.csv`, `cities.csv`, and `help_categories.csv`
  are lookup/reference tables sized to a small, realistic, curated list
  (real country/state/city names and a Saayam-style category taxonomy) --
  they are intentionally **not** scaled by `--count`, the same way a real
  database wouldn't have 400 countries.

At the default `--count 100`, generation looks like:

```
countries            5 rows   (fixed reference list)
states              12 rows   (fixed reference list)
cities              21 rows   (fixed reference list)
help_categories     18 rows   (fixed reference list)
users              100 rows
volunteer_details   60 rows   (60% of users)
user_skills        ~190 rows  (1-4 categories for 70% of users)
volunteer_locations 60 rows   (one per volunteer_details row)
user_locations      80 rows   (80% of users)
organizations      100 rows
```

At `--count 400`, `user_skills` alone comes out to 600-700+ rows, comfortably
covering the issue's "~400 rows per file" suggestion for the tables where
that's a meaningful target.

## Table relationships

```
users.country_id        -> countries.country_id
users.state_id           -> states.state_id
cities.state_id           -> states.state_id
states.country_id        -> countries.country_id   (NOT NULL)
volunteer_details.user_id -> users.user_id
user_skills.user_id       -> users.user_id
user_skills.cat_id        -> help_categories.cat_id
organizations.state_id    -> states.state_id
volunteer_locations.user_id -> volunteer_details.user_id   (NOT users.user_id directly)
user_locations.user_id     -> users.user_id
```

Notes:

- `volunteer_locations.user_id` references `volunteer_details.user_id`,
  not `users.user_id` directly -- every row in `volunteer_locations.csv`
  belongs to a user who already has a `volunteer_details.csv` row.
- `user_locations` and `volunteer_locations` don't store `city_id`/`state_id`
  columns; they store raw `geography(Point, 4326)` coordinates (`curr_loc`,
  `prev_loc`). This generator derives those coordinates by jittering the
  city centroid assigned to that user, so they land plausibly within the
  user's city rather than being unrelated random points.
- `users.language_1/2/3` (-> `supporting_languages`) and `users.user_status_id`
  (-> `user_status`) reference lookup tables that are outside issue #301's
  scope, so they're left blank/NULL in the generated data (both columns are
  nullable in the schema).

## Geographic consistency

Country/state/city combinations are drawn from a single curated mapping
(e.g. `United States -> California -> San Jose`, with that city's real
approximate centroid), so every user/organization's `state_id` + `city_name`
pair is always a valid, consistent combination -- never an unrelated
city/state/country mix. `curr_loc`/`prev_loc` coordinates are derived from
that same city's centroid (with a small random jitter), rather than being
independently randomized.

## Date/timestamp handling

All timestamps use `YYYY-MM-DD HH:MM:SS` (Postgres-compatible). Where a
table has both `created_at` and `last_updated_at` (or equivalent pairs, e.g.
`volunteer_details`, `user_skills`, `organizations`), `created_at` is
generated first and `last_updated_at` is always generated at or after it.

## Output location

CSV files are written to `data-analytics/mock-data-generation/` (or
wherever `--output-dir` points).

## Validation

A full validation pass (unique primary keys, no orphan foreign keys,
geographic consistency, timestamp ordering, and a real `COPY ... FROM` load
into a Postgres schema matching the actual DDL/wiki-documented column
types) was run against the generated output before this was submitted.
`geography(Point, 4326)` values use standard PostGIS WKT text
(`POINT(lon lat)`), which `ST_GeogFromText()`/`COPY` accept directly on a
Postgres instance with the `postgis` extension installed.

To re-run your own validation after regenerating data, check for:
- Duplicate values in each table's primary key column(s).
- Any `*_id` value in a child table that doesn't exist in the referenced
  parent table.
- Any `city_name` on a `users`/`organizations` row that isn't one of the
  cities listed for that row's `state_id` in `cities.csv`.
- `created_at <= last_updated_at` on every row where both columns exist.
- That every CSV loads via `COPY ... FROM ... WITH (FORMAT csv, HEADER true, NULL '')`
  into tables matching the current schema without a type or constraint error.
