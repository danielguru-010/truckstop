from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from routes.providers.routing import RoutingError


class GeocodeFuelStationsCommandTests(SimpleTestCase):
    @patch("routes.management.commands.geocode_fuel_stations.FuelStation")
    @patch("routes.management.commands.geocode_fuel_stations.NominatimGeocoder")
    def test_geocodes_missing_station_coordinates(self, mocked_geocoder, mocked_model):
        station = SimpleNamespace(
            id=7,
            address="123 Main St",
            city="Tulsa",
            state="OK",
            latitude=None,
            longitude=None,
            save=MagicMock(),
        )
        mocked_model.objects.filter.return_value.order_by.return_value = [station]
        mocked_geocoder.return_value.geocode.return_value = SimpleNamespace(
            latitude=36.15,
            longitude=-95.99,
        )

        call_command("geocode_fuel_stations", "--delay", "0")

        self.assertEqual(station.latitude, 36.15)
        self.assertEqual(station.longitude, -95.99)
        station.save.assert_called_once_with(update_fields=["latitude", "longitude"])

    @patch("routes.management.commands.geocode_fuel_stations.FuelStation")
    @patch("routes.management.commands.geocode_fuel_stations.NominatimGeocoder")
    def test_falls_back_to_city_when_address_is_not_found(self, mocked_geocoder, mocked_model):
        station = SimpleNamespace(
            id=8,
            address="I-44, EXIT 283 & US-69",
            city="Big Cabin",
            state="OK",
            latitude=None,
            longitude=None,
            save=MagicMock(),
        )
        mocked_model.objects.filter.return_value.order_by.return_value = [station]
        mocked_geocoder.return_value.geocode.side_effect = [
            RoutingError("address not found"),
            SimpleNamespace(latitude=36.55, longitude=-95.22),
        ]

        call_command("geocode_fuel_stations", "--delay", "0")

        self.assertEqual(station.latitude, 36.55)
        self.assertEqual(station.longitude, -95.22)
        mocked_geocoder.return_value.geocode.assert_any_call(
            "I-44, EXIT 283 & US-69, Big Cabin, OK, USA"
        )
        mocked_geocoder.return_value.geocode.assert_any_call("Big Cabin, OK, USA")
        station.save.assert_called_once_with(update_fields=["latitude", "longitude"])