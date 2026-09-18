from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from routes.providers.routing import Coordinate, NominatimGeocoder, OsrmRouter, RoutingError


class RoutingProviderTests(SimpleTestCase):
    @patch("routes.providers.routing.urlopen")
    def test_geocoder_returns_coordinate(self, mocked_urlopen):
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = None
        response.read.return_value = b'[{"lat": "35.2", "lon": "-97.4"}]'
        mocked_urlopen.return_value = response

        with patch("routes.providers.routing.json.load", return_value=[{"lat": "35.2", "lon": "-97.4"}]):
            coordinate = NominatimGeocoder().geocode("Oklahoma City, OK")

        self.assertEqual(coordinate, Coordinate(latitude=35.2, longitude=-97.4))

    @patch("routes.providers.routing.urlopen")
    def test_router_converts_distance_to_miles(self, mocked_urlopen):
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = None
        mocked_urlopen.return_value = response
        route_data = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 1609.344,
                    "duration": 3600,
                    "geometry": {"type": "LineString", "coordinates": []},
                }
            ],
        }

        with patch("routes.providers.routing.json.load", return_value=route_data):
            route = OsrmRouter().route(
                Coordinate(35.2, -97.4), Coordinate(36.1, -95.9)
            )

        self.assertEqual(route.distance_miles, 1.0)
        self.assertEqual(route.duration_seconds, 3600.0)

    @patch("routes.providers.routing.urlopen")
    def test_geocoder_rejects_empty_result(self, mocked_urlopen):
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = None
        mocked_urlopen.return_value = response

        with patch("routes.providers.routing.json.load", return_value=[]):
            with self.assertRaises(RoutingError):
                NominatimGeocoder().geocode("Not a real place")