import time

from django.core.management.base import BaseCommand

from routes.models import FuelStation
from routes.providers.routing import NominatimGeocoder, RoutingError


class Command(BaseCommand):
    help = "Geocode fuel stations that do not have coordinates yet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of stations to process; zero means all.",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.1,
            help="Seconds to wait between provider requests.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        delay = options["delay"]
        if limit < 0 or delay < 0:
            self.stderr.write("--limit and --delay must not be negative")
            return

        stations = FuelStation.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True,
        ).order_by("id")
        if limit:
            stations = stations[:limit]

        geocoder = NominatimGeocoder()
        updated = 0
        failed = 0
        for index, station in enumerate(stations):
            if index:
                time.sleep(delay)
            location = f"{station.address}, {station.city}, {station.state}, USA"
            try:
                coordinate = geocoder.geocode(location)
            except RoutingError as exc:
                failed += 1
                self.stderr.write(f"Could not geocode station {station.id}: {exc}")
                continue

            station.latitude = coordinate.latitude
            station.longitude = coordinate.longitude
            station.save(update_fields=["latitude", "longitude"])
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Geocoded {updated} station(s); {failed} lookup(s) failed."
            )
        )