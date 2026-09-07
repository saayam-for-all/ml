# Mock Data Generation - Issue #301

Generates fake data for the 10 tables we need for dashboard testing (states, users,
volunteer_details, cities, user_skills, volunteer_locations, user_locations,
countries, help_categories, organizations). Nothing real in here, all names/emails/etc
are Faker generated.

Heads up - the DB wiki has a note saying to hold off inserting data into `city` for now,
so double check with the team before this cities.csv actually gets loaded anywhere.

## Setup

```
pip install -r requirements.txt
python generate_mock_data.py
```

That's it, it'll spit out all 10 csvs in this same folder and print out row counts +
run some checks at the end (no orphan FKs, no duplicate PKs, etc).

## Row counts

Default is 400 users, 400 orgs, ~50% of users become volunteers, ~7 extra cities per
state (gets cities.csv to ~400 too). Countries/states/help_categories stay small on
purpose since those are basically fixed reference lists (only 50 real US states etc) -
padding them out with fake states didn't seem worth it just to hit a row count.

If you need different numbers just change NUM_USERS, NUM_ORGANIZATIONS,
VOLUNTEER_FRACTION, MAX_SKILLS_PER_USER, NUM_EXTRA_CITIES_PER_STATE at the top of
generate_mock_data.py. Everything else scales off of NUM_USERS automatically.

## How the tables connect

- countries -> states -> cities
- users need a state_id + country_id
- organizations need a state_id
- volunteer_details is just a subset of users (about half)
- user_skills links users/volunteers to help_categories
- user_locations - one row per user
- volunteer_locations - one row per volunteer, and this one points to
  volunteer_details.user_id, NOT users.user_id directly (easy to mess up)

## Notes to self

- user_id format follows the actual SID-00-XXX-XXX-XXX-XXX-XXX pattern from the users
  table trigger, org_id follows ORG-XXX-XXX-XXX-XXXX
- only fully built out cities/states for the US so the country->state->city chain
  stays realistic without needing geo data for every country
- lat/lng for user_locations and volunteer_locations are jittered around the user's
  assigned city so they land somewhere plausible instead of random points on a map
- timestamps are all created_at <= last_updated_at where both columns exist
