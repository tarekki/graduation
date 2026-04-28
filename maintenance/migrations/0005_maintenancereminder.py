import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("maintenance", "0004_alter_maintenancerecord_appointment"),
        ("cars", "0002_car_brand_color_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="MaintenanceReminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("due_date", models.DateField()),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_reminders",
                        to="cars.car",
                    ),
                ),
            ],
            options={"ordering": ("due_date",)},
        ),
    ]
