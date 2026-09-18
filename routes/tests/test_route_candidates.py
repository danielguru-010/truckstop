from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from routes.services.route_candidates import stations_on_route


class RouteCandidateTests(SimpleTestCase):
    route_geometry = {
        "type": "LineString",
        "coordinates": [[-97.5, 35.0], [-97.5, 36.0], [-97.5, 37.0]],
    }

    def test_returns_stations_in_route_order(self):
        stations = [
            SimpleNamespace(
                id=2,
                name="North",
                city="North City",
                state="OK",
                latitude=36.95,
                longitude=-97.5,
                retail_price=Decimal("3.10"),
            ),
            SimpleNamespace(
                id=1,
                name="South",
                city="South City",
                state="OK",
                latitude=35.05,
                longitude=-97.5,
                retail_price=Decimal("3.25"),
            ),
        ]

        candidates = stations_on_route(self.route_geometry, stations)

        self.assertEqual([candidate.station_id for candidate in candidates], [1, 2])
        self.assertLess(candidates[0].distance_miles, candidates[1].distance_miles)

    def test_ignores_stations_outside_route_corridor(self):
        station = SimpleNamespace(
            id=3,
            name="Far away",
            city="Far City",
            state="OK",
            latitude=36.0,
            longitude=-98.5,
            retail_price=Decimal("2.99"),
        )

        self.assertEqual(stations_on_route(self.route_geometry, [station]), [])