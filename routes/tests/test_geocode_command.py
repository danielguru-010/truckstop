from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase


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