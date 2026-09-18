from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase


class RouteViewTests(SimpleTestCase):
    def test_rejects_invalid_json(self):
        response = self.client.post(
            "/route/", data="not-json", content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Request body must be valid JSON")

    def test_requires_start_and_finish(self):
        response = self.client.post(
            "/route/", data={"start": "Oklahoma City, OK"}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("finish", response.json()["error"])

    @patch("routes.views.RoutePlanner.plan")
    def test_returns_route_and_fuel_summary(self, mocked_plan):
        mocked_plan.return_value = {
            "route": {
                "distance_miles": 205.5,
                "duration_seconds": 12300.0,
                "geometry": {"type": "LineString", "coordinates": []},
            },
            "fuel_stops": [
                {
                    "station_id": 12,
                    "name": "Example Fuel",
                    "city": "Lawton",
                    "state": "OK",
                    "distance_miles": 95.0,
                    "price_per_gallon": Decimal("3.1299"),
                    "gallons": 5.0,
                    "cost": Decimal("15.65"),
                }
            ],
            "total_gallons": 5.0,
            "total_cost": Decimal("15.65"),
        }

        response = self.client.post(
            "/route/",
            data={"start": "Oklahoma City, OK", "finish": "Dallas, TX"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_cost"], "15.65")
        self.assertEqual(response.json()["fuel_stops"][0]["cost"], "15.65")
        mocked_plan.assert_called_once_with("Oklahoma City, OK", "Dallas, TX")