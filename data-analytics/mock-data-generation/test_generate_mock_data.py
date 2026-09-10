"""Tests for #301 Virginia analytics mock-data generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate_mock_data as gen


class MockDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = gen.generate_all(25, seed=7)

    def test_expected_tables_exist(self):
        self.assertEqual(
            set(self.data),
            {
                "countries",
                "states",
                "cities",
                "help_categories",
                "users",
                "volunteer_details",
                "user_skills",
                "volunteer_locations",
                "user_locations",
                "organizations",
            },
        )

    def test_row_counts(self):
        for key in (
            "countries",
            "states",
            "cities",
            "users",
            "volunteer_details",
            "user_skills",
            "volunteer_locations",
            "user_locations",
            "organizations",
        ):
            self.assertEqual(len(self.data[key]), 25, key)
        self.assertGreaterEqual(len(self.data["help_categories"]), 10)

    def test_headers_match_schema_contract(self):
        self.assertEqual(list(self.data["users"][0]), gen.USERS_FIELDS)
        self.assertEqual(list(self.data["states"][0]), gen.STATES_FIELDS)
        self.assertEqual(list(self.data["cities"][0]), gen.CITIES_FIELDS)
        self.assertEqual(list(self.data["countries"][0]), gen.COUNTRIES_FIELDS)
        self.assertIn("state_id", self.data["organizations"][0])
        self.assertIn("size", self.data["organizations"][0])
        self.assertIn("rating", self.data["organizations"][0])
        self.assertIn("lattitude", self.data["cities"][0])

    def test_validator_accepts_generated_data(self):
        self.assertEqual(gen.validate_dataset(self.data), [])

    def test_volunteer_locations_require_volunteer_details(self):
        volunteer_ids = {row["user_id"] for row in self.data["volunteer_details"]}
        for row in self.data["volunteer_locations"]:
            self.assertIn(row["user_id"], volunteer_ids)

    def test_foreign_keys(self):
        country_ids = {str(row["country_id"]) for row in self.data["countries"]}
        state_ids = {row["state_id"] for row in self.data["states"]}
        user_ids = {row["user_id"] for row in self.data["users"]}
        cat_ids = {row["cat_id"] for row in self.data["help_categories"]}
        for row in self.data["states"]:
            self.assertIn(str(row["country_id"]), country_ids)
        for row in self.data["cities"]:
            self.assertIn(row["state_id"], state_ids)
        for row in self.data["users"]:
            self.assertIn(row["state_id"], state_ids)
            self.assertIn(str(row["country_id"]), country_ids)
            self.assertTrue(row["user_id"].startswith("MOCK-USR-"))
        for row in self.data["user_skills"]:
            self.assertIn(row["user_id"], user_ids)
            self.assertIn(row["cat_id"], cat_ids)
        for row in self.data["organizations"]:
            self.assertIn(row["state_id"], state_ids)
            self.assertIn(row["cat_id"], cat_ids)

    def test_synthetic_contact_info(self):
        for row in self.data["users"]:
            self.assertTrue(row["primary_email_address"].endswith("@mock.saayam.test"))
            self.assertIn("555", row["primary_phone_number"])
            self.assertTrue(row["addr_ln1"].endswith("Mock Street"))
        for row in self.data["organizations"]:
            self.assertTrue(row["email"].endswith("@mock-org.test"))
            self.assertTrue(row["web_url"].endswith(".example.test"))

    def test_write_and_validate_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            self.assertEqual(
                gen.main(["--rows", "12", "--seed", "3", "--output-dir", str(output)]),
                0,
            )
            self.assertEqual(
                gen.main(["--validate-only", "--output-dir", str(output)]),
                0,
            )
            self.assertTrue((output / "states.csv").exists())
            self.assertTrue((output / "countries.csv").exists())
            self.assertTrue((output / "cities.csv").exists())
            self.assertTrue((output / "help_categories.csv").exists())


if __name__ == "__main__":
    unittest.main()
