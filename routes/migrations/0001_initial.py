from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FuelStation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("opis_id", models.CharField(max_length=32)),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=128)),
                ("state", models.CharField(max_length=2)),
                ("rack_id", models.CharField(max_length=32)),
                ("retail_price", models.DecimalField(decimal_places=4, max_digits=7)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["state", "city"], name="routes_fuel_state_4b7a9e_idx"),
                    models.Index(fields=["retail_price"], name="routes_fuel_retail_1b8d67_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("opis_id", "name", "address", "city", "state", "rack_id"),
                        name="unique_fuel_station_source_row",
                    )
                ],
            },
        ),
    ]