"""
Maintenance serializers.

Conventions:
- Write side: accept `<field>Id` (camelCase) → mapped to FK instances via
  `PrimaryKeyRelatedField(source=..., write_only=True)`.
- Read side: nested objects (id + name/name-ish fields) using mini serializers
  defined here or in `lookups.serializers`.
- `owner`/`mechanic` on appointments and records are auto-assigned server-side.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from cars.models import Car
from cars.permissions import user_is_admin, user_is_mechanic
from lookups.serializers import BrandMiniSerializer, UserMiniSerializer

from .models import (
    MaintenanceAppointment,
    MaintenanceAppointmentStatus,
    MaintenanceRecord,
    MaintenanceReminder,
    MileageLog,
)

User = get_user_model()


class CarMiniSerializer(serializers.ModelSerializer):
    """Minimal car representation used across maintenance read payloads."""

    brand = BrandMiniSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ("id", "brand", "model", "plate_number")


class MileageLogSerializer(serializers.ModelSerializer):
    """`carId` in, nested `car` out."""

    car_id = serializers.PrimaryKeyRelatedField(
        source="car",
        queryset=Car.objects.select_related("owner", "brand"),
        write_only=True,
        error_messages={"does_not_exist": "Invalid carId.", "incorrect_type": "carId must be an integer."},
    )
    car = CarMiniSerializer(read_only=True)

    class Meta:
        model = MileageLog
        fields = ("id", "car_id", "car", "mileage", "recorded_at", "note")
        read_only_fields = ("id", "car", "recorded_at")

    def validate_mileage(self, value: int) -> int:
        if value > 2_000_000:
            raise serializers.ValidationError("Mileage value is unrealistically high.")
        return value

    def validate_car_id(self, car: Car) -> Car:
        request = self.context.get("request")
        if request and not user_is_admin(request.user) and car.owner_id != request.user.id:
            raise serializers.ValidationError(
                "You can only add or link mileage logs to your own cars."
            )
        return car


class MaintenanceReminderSerializer(serializers.ModelSerializer):
    """`carId` in, nested `car` out."""

    car_id = serializers.PrimaryKeyRelatedField(
        source="car",
        queryset=Car.objects.select_related("owner", "brand"),
        write_only=True,
        error_messages={"does_not_exist": "Invalid carId.", "incorrect_type": "carId must be an integer."},
    )
    car = CarMiniSerializer(read_only=True)

    class Meta:
        model = MaintenanceReminder
        fields = ("id", "car_id", "car", "title", "due_date", "notes", "created_at")
        read_only_fields = ("id", "car", "created_at")

    def validate_title(self, value):
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Title is required.")
        return text[:120]

    def validate_due_date(self, value):
        if self.instance is None and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_car_id(self, car: Car) -> Car:
        request = self.context.get("request")
        if request and not user_is_admin(request.user) and car.owner_id != request.user.id:
            raise serializers.ValidationError(
                "You can only set reminders for your own cars."
            )
        return car


class AppointmentReadSerializer(serializers.ModelSerializer):
    """Read payload: nested car, owner, mechanic."""

    car = CarMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)
    mechanic = UserMiniSerializer(read_only=True)

    class Meta:
        model = MaintenanceAppointment
        fields = (
            "id",
            "car",
            "owner",
            "mechanic",
            "service_type",
            "appointment_date",
            "status",
            "description",
            "created_at",
        )
        read_only_fields = fields


class MaintenanceAppointmentSerializer(serializers.ModelSerializer):
    """
    Write: `carId` (required) and optional `mechanicId`. `owner` is always the
    logged-in user. Read: nested car/owner/mechanic.
    """

    car_id = serializers.PrimaryKeyRelatedField(
        source="car",
        queryset=Car.objects.select_related("owner", "brand"),
        write_only=True,
        error_messages={"does_not_exist": "Invalid carId.", "incorrect_type": "carId must be an integer."},
    )
    mechanic_id = serializers.PrimaryKeyRelatedField(
        source="mechanic",
        queryset=User.objects.select_related("role"),
        write_only=True,
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "Invalid mechanicId.", "incorrect_type": "mechanicId must be an integer."},
    )

    car = CarMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)
    mechanic = UserMiniSerializer(read_only=True)

    class Meta:
        model = MaintenanceAppointment
        fields = (
            "id",
            "car_id",
            "car",
            "owner",
            "mechanic_id",
            "mechanic",
            "service_type",
            "appointment_date",
            "status",
            "description",
            "created_at",
        )
        read_only_fields = ("id", "car", "owner", "mechanic", "created_at")

    def validate_service_type(self, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Service type is required.")
        return text[:120]

    def validate_appointment_date(self, value):
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value

    def validate_car_id(self, car: Car) -> Car:
        request = self.context.get("request")
        if request and not user_is_admin(request.user) and car.owner_id != request.user.id:
            raise serializers.ValidationError(
                "You can only book maintenance for your own cars."
            )
        return car

    def validate_mechanic_id(self, mechanic):
        if mechanic is None:
            return mechanic
        role = getattr(mechanic, "role", None)
        role_code = getattr(role, "code", None)
        if role_code != "MECHANIC":
            raise serializers.ValidationError("mechanicId must reference a MECHANIC user.")
        return mechanic


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """
    Create: client sends `appointmentId` + service fields; server sets `car` and
    `mechanic` from the appointment. Update: cannot change appointment/car/mechanic.
    """

    appointment_id = serializers.PrimaryKeyRelatedField(
        source="appointment",
        queryset=MaintenanceAppointment.objects.select_related("car", "car__owner", "mechanic"),
        write_only=True,
        error_messages={"does_not_exist": "Invalid appointmentId.", "incorrect_type": "appointmentId must be an integer."},
    )
    appointment = AppointmentReadSerializer(read_only=True)
    car = CarMiniSerializer(read_only=True)
    mechanic = UserMiniSerializer(read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = (
            "id",
            "appointment_id",
            "appointment",
            "car",
            "mechanic",
            "service_done",
            "cost",
            "notes",
            "service_date",
            "created_at",
        )
        read_only_fields = ("id", "appointment", "car", "mechanic", "created_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields.pop("appointment_id", None)

    def validate_service_done(self, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Service done is required.")
        return text[:150]

    def validate_cost(self, value):
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative.")
        return value

    def validate_service_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Service date cannot be in the future.")
        return value

    def validate_appointment_id(self, appointment: MaintenanceAppointment):
        if self.instance is not None:
            return appointment

        if MaintenanceRecord.objects.filter(appointment_id=appointment.pk).exists():
            raise serializers.ValidationError(
                "A maintenance record already exists for this appointment."
            )
        if appointment.status != MaintenanceAppointmentStatus.COMPLETED:
            raise serializers.ValidationError(
                "A record can only be created when the appointment status is completed."
            )
        if appointment.mechanic_id is None:
            raise serializers.ValidationError(
                "The appointment must have an assigned mechanic before creating a record."
            )

        request = self.context.get("request")
        if request and user_is_mechanic(request.user) and not user_is_admin(request.user):
            if appointment.mechanic_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only create a record for appointments assigned to you."
                )
        return appointment

    def create(self, validated_data):
        appointment = validated_data.pop("appointment")
        validated_data["appointment"] = appointment
        validated_data["car"] = appointment.car
        validated_data["mechanic"] = appointment.mechanic
        return MaintenanceRecord.objects.create(**validated_data)
