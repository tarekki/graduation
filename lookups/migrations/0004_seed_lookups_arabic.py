from django.db import migrations

ROLE_AR = {
    "ADMIN": "مدير",
    "OWNER": "مالك",
    "CUSTOMER": "عميل",
    "MECHANIC": "ميكانيكي",
}

BRAND_AR = {
    "Toyota": "تويوتا",
    "Honda": "هوندا",
    "Ford": "فورد",
    "BMW": "بي إم دبليو",
    "Mercedes-Benz": "مرسيدس بنز",
    "Hyundai": "هيونداي",
    "Kia": "كيا",
    "Volkswagen": "فولكس فاجن",
    "Nissan": "نيسان",
    "Other": "أخرى",
}

COLOR_AR = {
    "White": "أبيض",
    "Black": "أسود",
    "Silver": "فضي",
    "Gray": "رمادي",
    "Red": "أحمر",
    "Blue": "أزرق",
    "Other": "أخرى",
}


def seed_arabic(apps, schema_editor):
    Role = apps.get_model("lookups", "Role")
    CarBrand = apps.get_model("lookups", "CarBrand")
    CarColor = apps.get_model("lookups", "CarColor")

    for code, name_ar in ROLE_AR.items():
        Role.objects.filter(code=code).update(name_ar=name_ar)

    for name, name_ar in BRAND_AR.items():
        CarBrand.objects.filter(name=name).update(name_ar=name_ar)

    for name, name_ar in COLOR_AR.items():
        CarColor.objects.filter(name=name).update(name_ar=name_ar)


def clear_arabic(apps, schema_editor):
    for model_name in ("Role", "CarBrand", "CarColor"):
        apps.get_model("lookups", model_name).objects.update(name_ar="")


class Migration(migrations.Migration):

    dependencies = [
        ("lookups", "0003_carbrand_name_ar_carcolor_name_ar_role_name_ar"),
    ]

    operations = [
        migrations.RunPython(seed_arabic, clear_arabic),
    ]
