# utils.py
# helper functions + reference data used by generate_mock_data.py
# schema is based on the current version of the DB wiki (post 8/17 pluralization)

import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# countries table
COUNTRIES = [
    {"country_name": "United States", "phone_code": "+1", "country_code": "US", "is_eu_member": False},
    {"country_name": "Canada", "phone_code": "+1", "country_code": "CA", "is_eu_member": False},
    {"country_name": "India", "phone_code": "+91", "country_code": "IN", "is_eu_member": False},
    {"country_name": "United Kingdom", "phone_code": "+44", "country_code": "GB", "is_eu_member": False},
    {"country_name": "Germany", "phone_code": "+49", "country_code": "DE", "is_eu_member": True},
]

# real US states + 1-3 real cities per state w/ approx lat/lng, so the
# country -> state -> city chain actually makes sense. extra synthetic
# cities get jittered around one of these points, see jitter_coordinates()
US_STATES = [
    ("Alabama", "AL", [("Birmingham", 33.5207, -86.8025), ("Montgomery", 32.3668, -86.3000)]),
    ("Alaska", "AK", [("Anchorage", 61.2181, -149.9003)]),
    ("Arizona", "AZ", [("Phoenix", 33.4484, -112.0740), ("Tucson", 32.2226, -110.9747)]),
    ("Arkansas", "AR", [("Little Rock", 34.7465, -92.2896)]),
    ("California", "CA", [("San Jose", 37.3382, -121.8863), ("Los Angeles", 34.0522, -118.2437), ("San Francisco", 37.7749, -122.4194)]),
    ("Colorado", "CO", [("Denver", 39.7392, -104.9903)]),
    ("Connecticut", "CT", [("Hartford", 41.7658, -72.6734)]),
    ("Delaware", "DE", [("Wilmington", 39.7391, -75.5398)]),
    ("Florida", "FL", [("Miami", 25.7617, -80.1918), ("Orlando", 28.5383, -81.3792)]),
    ("Georgia", "GA", [("Atlanta", 33.7490, -84.3880)]),
    ("Hawaii", "HI", [("Honolulu", 21.3069, -157.8583)]),
    ("Idaho", "ID", [("Boise", 43.6150, -116.2023)]),
    ("Illinois", "IL", [("Chicago", 41.8781, -87.6298)]),
    ("Indiana", "IN", [("Indianapolis", 39.7684, -86.1581)]),
    ("Iowa", "IA", [("Des Moines", 41.5868, -93.6250)]),
    ("Kansas", "KS", [("Wichita", 37.6872, -97.3301)]),
    ("Kentucky", "KY", [("Louisville", 38.2527, -85.7585)]),
    ("Louisiana", "LA", [("New Orleans", 29.9511, -90.0715)]),
    ("Maine", "ME", [("Portland", 43.6591, -70.2568)]),
    ("Maryland", "MD", [("Baltimore", 39.2904, -76.6122)]),
    ("Massachusetts", "MA", [("Boston", 42.3601, -71.0589)]),
    ("Michigan", "MI", [("Detroit", 42.3314, -83.0458)]),
    ("Minnesota", "MN", [("Minneapolis", 44.9778, -93.2650)]),
    ("Mississippi", "MS", [("Jackson", 32.2988, -90.1848)]),
    ("Missouri", "MO", [("Kansas City", 39.0997, -94.5786)]),
    ("Montana", "MT", [("Billings", 45.7833, -108.5007)]),
    ("Nebraska", "NE", [("Omaha", 41.2565, -95.9345)]),
    ("Nevada", "NV", [("Las Vegas", 36.1699, -115.1398)]),
    ("New Hampshire", "NH", [("Manchester", 42.9956, -71.4548)]),
    ("New Jersey", "NJ", [("Newark", 40.7357, -74.1724)]),
    ("New Mexico", "NM", [("Albuquerque", 35.0844, -106.6504)]),
    ("New York", "NY", [("New York City", 40.7128, -74.0060), ("Buffalo", 42.8864, -78.8784)]),
    ("North Carolina", "NC", [("Charlotte", 35.2271, -80.8431)]),
    ("North Dakota", "ND", [("Fargo", 46.8772, -96.7898)]),
    ("Ohio", "OH", [("Columbus", 39.9612, -82.9988)]),
    ("Oklahoma", "OK", [("Oklahoma City", 35.4676, -97.5164)]),
    ("Oregon", "OR", [("Portland", 45.5051, -122.6750)]),
    ("Pennsylvania", "PA", [("Philadelphia", 39.9526, -75.1652)]),
    ("Rhode Island", "RI", [("Providence", 41.8240, -71.4128)]),
    ("South Carolina", "SC", [("Columbia", 34.0007, -81.0348)]),
    ("South Dakota", "SD", [("Sioux Falls", 43.5460, -96.7313)]),
    ("Tennessee", "TN", [("Nashville", 36.1627, -86.7816)]),
    ("Texas", "TX", [("Dallas", 32.7767, -96.7970), ("Austin", 30.2672, -97.7431), ("Houston", 29.7604, -95.3698)]),
    ("Utah", "UT", [("Salt Lake City", 40.7608, -111.8910)]),
    ("Vermont", "VT", [("Burlington", 44.4759, -73.2121)]),
    ("Virginia", "VA", [("Richmond", 37.5407, -77.4360), ("Arlington", 38.8816, -77.0910)]),
    ("Washington", "WA", [("Seattle", 47.6062, -122.3321)]),
    ("West Virginia", "WV", [("Charleston", 38.3498, -81.6326)]),
    ("Wisconsin", "WI", [("Milwaukee", 43.0389, -87.9065)]),
    ("Wyoming", "WY", [("Cheyenne", 41.1400, -104.8202)]),
]

HELP_CATEGORY_TOPICS = [
    "Housing Assistance", "Food Support", "Medical & Health", "Employment & Job Training",
    "Education & Tutoring", "Transportation", "Childcare", "Elder Care",
    "Disaster Relief", "Mental Health Support", "Legal Aid", "Financial Counseling",
    "Clothing Donations", "Home Repair", "Language Translation",
]

SKILL_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
ORG_TYPES = ["non_profit", "for_profit"]
ORG_SIZES = ["small", "medium", "large"]


# matches the real generate_sid() trigger: SID-00-XXX-XXX-XXX-XXX-XXX
def generate_sid(seq_id: int) -> str:
    padded = str(seq_id).zfill(15)
    groups = [padded[i:i + 3] for i in range(0, 15, 3)]
    return "SID-00-" + "-".join(groups)


# matches generate_org_id(): ORG-XXX-XXX-XXX-XXXX
def generate_org_id(seq_id: int) -> str:
    padded = str(seq_id).zfill(13)
    return f"ORG-{padded[0:3]}-{padded[3:6]}-{padded[6:9]}-{padded[9:13]}"


# nudges a lat/lng a bit so it stays roughly within the same city/state
def jitter_coordinates(lat: float, lng: float, max_delta: float = 0.15):
    return (
        round(lat + random.uniform(-max_delta, max_delta), 6),
        round(lng + random.uniform(-max_delta, max_delta), 6),
    )


def random_datetime_between(start: datetime, end: datetime) -> datetime:
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


# created_at always <= last_updated_at
def created_and_updated_pair(start: datetime, end: datetime):
    created = random_datetime_between(start, end)
    updated = random_datetime_between(created, end)
    return created, updated


def pg_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
