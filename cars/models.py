from django.db import models


class Car(models.Model):
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cars",
    )
    brand = models.ForeignKey(
        "lookups.CarBrand",
        on_delete=models.PROTECT,
        related_name="cars",
    )
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    plate_number = models.CharField(max_length=30, unique=True)
    color = models.ForeignKey(
        "lookups.CarColor",
        on_delete=models.SET_NULL,
        related_name="cars",
        blank=True,
        null=True,
    )
    mileage = models.PositiveIntegerField(
        help_text="Odometer reading for display/optional tracking only. Do not use for maintenance reminders—use date-based reminders instead.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand.name} {self.model} ({self.plate_number})"
