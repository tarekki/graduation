from django.db import migrations


def seed_lookups(apps, schema_editor):
    Role = apps.get_model("lookups", "Role")
    CarBrand = apps.get_model("lookups", "CarBrand")
    CarColor = apps.get_model("lookups", "CarColor")

    for code, name in (
        ("ADMIN", "Admin"),
        ("OWNER", "Owner"),
        ("CUSTOMER", "Customer"),
        ("MECHANIC", "Mechanic"),
    ):
        Role.objects.get_or_create(code=code, defaults={"name": name})

    for name in (
        "Toyota",
        "Honda",
        "Ford",
        "BMW",
        "Mercedes-Benz",
        "Hyundai",
        "Kia",
        "Volkswagen",
        "Nissan",
        "Other",
    ):
        CarBrand.objects.get_or_create(name=name)

    for name in ("White", "Black", "Silver", "Gray", "Red", "Blue", "Other"):
        CarColor.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("lookups", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_lookups, migrations.RunPython.noop),
    ]
