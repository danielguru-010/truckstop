import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from routes.models import FuelStation


REQUIRED_COLUMNS = {
    "OPIS Truckstop ID",
    "Truckstop Name",
    "Address",
    "City",
    "State",
    "Rack ID",
    "Retail Price",
}


class Command(BaseCommand):
    help = "Import fuel prices from the assessment CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        if not csv_path.is_file():
            raise CommandError(f"CSV file does not exist: {csv_path}")

        imported = 0
        updated = 0
        with csv_path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            columns = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - columns
            if missing:
                missing_columns = ", ".join(sorted(missing))
                raise CommandError(f"CSV is missing required columns: {missing_columns}")

            for line_number, row in enumerate(reader, start=2):
                try:
                    price = Decimal(row["Retail Price"])
                except (InvalidOperation, TypeError):
                    raise CommandError(f"Invalid retail price on CSV line {line_number}")

                identity = {
                    "opis_id": row["OPIS Truckstop ID"].strip(),
                    "name": row["Truckstop Name"].strip(),
                    "address": row["Address"].strip(),
                    "city": row["City"].strip(),
                    "state": row["State"].strip().upper(),
                    "rack_id": row["Rack ID"].strip(),
                }
                _, created = FuelStation.objects.update_or_create(
                    **identity,
                    defaults={"retail_price": price},
                )
                imported += created
                updated += not created

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported} station(s); updated {updated} station(s)."
            )
        )