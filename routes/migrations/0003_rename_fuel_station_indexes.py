from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("routes", "0002_fuelstation_coordinates")]

    operations = [
        migrations.RenameIndex(
            model_name="fuelstation",
            old_name="routes_fuel_state_4b7a9e_idx",
            new_name="routes_fuel_state_34c75b_idx",
        ),
        migrations.RenameIndex(
            model_name="fuelstation",
            old_name="routes_fuel_retail_1b8d67_idx",
            new_name="routes_fuel_retail__88f3a7_idx",
        ),
        migrations.RenameIndex(
            model_name="fuelstation",
            old_name="routes_fuel_latitude_9d0b99_idx",
            new_name="routes_fuel_latitud_203dad_idx",
        ),
    ]