from django.db import models


class FuelStation(models.Model):
    opis_id = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2)
    rack_id = models.CharField(max_length=32)
    retail_price = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "opis_id",
                    "name",
                    "address",
                    "city",
                    "state",
                    "rack_id",
                ],
                name="unique_fuel_station_source_row",
            )
        ]
        indexes = [
            models.Index(fields=["state", "city"]),
            models.Index(fields=["retail_price"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.city}, {self.state})"