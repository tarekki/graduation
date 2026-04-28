import django.db.models.deletion
from django.db import migrations, models


def migrate_car_lookups(apps, schema_editor):
    Car = apps.get_model("cars", "Car")
    CarBrand = apps.get_model("lookups", "CarBrand")
    CarColor = apps.get_model("lookups", "CarColor")

    for car in Car.objects.all():
        bname = (getattr(car, "brand", None) or "Other")[:100]
        bname = str(bname).strip() or "Other"
        brand_obj, _ = CarBrand.objects.get_or_create(name=bname)
        car.brand_new_id = brand_obj.pk

        col = getattr(car, "color", None)
        if col:
            cname = str(col)[:64]
            cobj, _ = CarColor.objects.get_or_create(name=cname)
            car.color_new_id = cobj.pk
        car.save()


class Migration(migrations.Migration):

    dependencies = [
        ("cars", "0001_initial"),
        ("lookups", "0002_seed_lookups"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="brand_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lookups.carbrand",
            ),
        ),
        migrations.AddField(
            model_name="car",
            name="color_new",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="lookups.carcolor",
            ),
        ),
        migrations.RunPython(migrate_car_lookups, migrations.RunPython.noop),
        migrations.RemoveField(model_name="car", name="brand"),
        migrations.RemoveField(model_name="car", name="color"),
        migrations.RenameField(model_name="car", old_name="brand_new", new_name="brand"),
        migrations.RenameField(model_name="car", old_name="color_new", new_name="color"),
        migrations.AlterField(
            model_name="car",
            name="brand",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cars",
                to="lookups.carbrand",
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cars",
                to="lookups.carcolor",
            ),
        ),
    ]
