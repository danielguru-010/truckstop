from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("routes", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="fuelstation",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="fuelstation",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="fuelstation",
            index=models.Index(
                fields=["latitude", "longitude"],
                name="routes_fuel_latitude_9d0b99_idx",
            ),
        ),
    ]