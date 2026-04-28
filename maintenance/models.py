from django.db import models


class MileageLog(models.Model):
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="mileage_logs",
    )
    mileage = models.PositiveIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.car} - {self.mileage} km"


class MaintenanceReminder(models.Model):
    """Date-based maintenance reminder (not driven by mileage accuracy)."""

    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="maintenance_reminders",
    )
    title = models.CharField(max_length=120)
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("due_date",)

    def __str__(self):
        return f"{self.car} — {self.title} ({self.due_date})"


class MaintenanceAppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class MaintenanceAppointment(models.Model):
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="maintenance_appointments",
    )
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="owner_appointments",
    )
    mechanic = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="mechanic_appointments",
        blank=True,
        null=True,
    )
    service_type = models.CharField(max_length=120)
    appointment_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=MaintenanceAppointmentStatus.choices,
        default=MaintenanceAppointmentStatus.PENDING,
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} - {self.service_type} ({self.status})"


class MaintenanceRecord(models.Model):
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    appointment = models.OneToOneField(
        "maintenance.MaintenanceAppointment",
        on_delete=models.CASCADE,
        related_name="record",
    )
    mechanic = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    service_done = models.CharField(max_length=150)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    service_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} - {self.service_done} ({self.service_date.date()})"
