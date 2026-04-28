"""
POST-only maintenance endpoints.

Four modules, each following the same shape:
    POST /<resource>/list/
    POST /<resource>/get/
    POST /<resource>/create/
    POST /<resource>/update/
    POST /<resource>/delete/

Role-based queryset filtering is encapsulated in small scope mixins so the
base CRUD views stay identical across modules.
"""
from django.db.models import Q

from cars.permissions import user_is_admin, user_is_mechanic, user_is_owner
from common.views import (
    BaseCreateAPIView,
    BaseDeleteAPIView,
    BaseGetAPIView,
    BaseListAPIView,
    BaseUpdateAPIView,
)

from .models import (
    MaintenanceAppointment,
    MaintenanceRecord,
    MaintenanceReminder,
    MileageLog,
)
from .permissions import IsAdminOrOwnsReminderCar, IsMaintenanceRecordPermission
from .serializers import (
    MaintenanceAppointmentSerializer,
    MaintenanceRecordSerializer,
    MaintenanceReminderSerializer,
    MileageLogSerializer,
)


# ---------- Mileage logs ----------


class _MileageLogScopeMixin:
    def get_queryset(self):
        qs = (
            MileageLog.objects
            .select_related("car", "car__brand")
            .order_by("-recorded_at", "-id")
        )
        user = self.request.user
        if user_is_admin(user):
            return qs
        return qs.filter(car__owner_id=user.pk)


class MileageLogListView(_MileageLogScopeMixin, BaseListAPIView):
    serializer_class = MileageLogSerializer
    list_success_message = "Mileage logs fetched successfully"


class MileageLogGetView(_MileageLogScopeMixin, BaseGetAPIView):
    serializer_class = MileageLogSerializer
    get_success_message = "Mileage log fetched successfully"


class MileageLogCreateView(_MileageLogScopeMixin, BaseCreateAPIView):
    serializer_class = MileageLogSerializer
    create_success_message = "Mileage log created successfully"


class MileageLogUpdateView(_MileageLogScopeMixin, BaseUpdateAPIView):
    serializer_class = MileageLogSerializer
    update_success_message = "Mileage log updated successfully"


class MileageLogDeleteView(_MileageLogScopeMixin, BaseDeleteAPIView):
    serializer_class = MileageLogSerializer
    delete_success_message = "Mileage log deleted successfully"


# ---------- Reminders ----------


class _ReminderScopeMixin:
    permission_classes_extra = [IsAdminOrOwnsReminderCar]

    def get_permissions(self):
        base = list(super().get_permissions())
        base.extend([cls() for cls in self.permission_classes_extra])
        return base

    def get_queryset(self):
        qs = (
            MaintenanceReminder.objects
            .select_related("car", "car__brand")
            .order_by("due_date", "id")
        )
        user = self.request.user
        if user_is_admin(user):
            return qs
        return qs.filter(car__owner_id=user.pk)


class ReminderListView(_ReminderScopeMixin, BaseListAPIView):
    serializer_class = MaintenanceReminderSerializer
    list_success_message = "Reminders fetched successfully"


class ReminderGetView(_ReminderScopeMixin, BaseGetAPIView):
    serializer_class = MaintenanceReminderSerializer
    get_success_message = "Reminder fetched successfully"


class ReminderCreateView(_ReminderScopeMixin, BaseCreateAPIView):
    serializer_class = MaintenanceReminderSerializer
    create_success_message = "Reminder created successfully"


class ReminderUpdateView(_ReminderScopeMixin, BaseUpdateAPIView):
    serializer_class = MaintenanceReminderSerializer
    update_success_message = "Reminder updated successfully"


class ReminderDeleteView(_ReminderScopeMixin, BaseDeleteAPIView):
    serializer_class = MaintenanceReminderSerializer
    delete_success_message = "Reminder deleted successfully"


# ---------- Appointments ----------


class _AppointmentScopeMixin:
    def get_queryset(self):
        # If the read serializer starts exposing role/owner-of-car info
        # (e.g. `mechanic.roleName`, `car.owner.firstName`), re-add
        # `mechanic__role` and/or `car__owner` here to keep it single-query.
        qs = (
            MaintenanceAppointment.objects
            .select_related("car", "car__brand", "owner", "mechanic")
            .order_by("-appointment_date", "-id")
        )
        user = self.request.user
        if user_is_admin(user):
            return qs
        return qs.filter(Q(owner_id=user.pk) | Q(mechanic_id=user.pk))


class AppointmentListView(_AppointmentScopeMixin, BaseListAPIView):
    serializer_class = MaintenanceAppointmentSerializer
    list_success_message = "Appointments fetched successfully"


class AppointmentGetView(_AppointmentScopeMixin, BaseGetAPIView):
    serializer_class = MaintenanceAppointmentSerializer
    get_success_message = "Appointment fetched successfully"


class AppointmentCreateView(_AppointmentScopeMixin, BaseCreateAPIView):
    serializer_class = MaintenanceAppointmentSerializer
    create_success_message = "Appointment created successfully"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AppointmentUpdateView(_AppointmentScopeMixin, BaseUpdateAPIView):
    serializer_class = MaintenanceAppointmentSerializer
    update_success_message = "Appointment updated successfully"


class AppointmentDeleteView(_AppointmentScopeMixin, BaseDeleteAPIView):
    serializer_class = MaintenanceAppointmentSerializer
    delete_success_message = "Appointment deleted successfully"


# ---------- Records ----------


class _RecordScopeMixin:
    permission_classes_extra = [IsMaintenanceRecordPermission]

    def get_permissions(self):
        base = list(super().get_permissions())
        base.extend([cls() for cls in self.permission_classes_extra])
        return base

    def get_queryset(self):
        qs = (
            MaintenanceRecord.objects
            .select_related(
                "appointment",
                "appointment__car",
                "appointment__car__brand",
                "appointment__owner",
                "appointment__mechanic",
                "car",
                "car__brand",
                "mechanic",
            )
            .order_by("-service_date", "-id")
        )
        user = self.request.user
        uid = user.pk
        if uid is None:
            return MaintenanceRecord.objects.none()
        if user_is_admin(user):
            return qs
        if user_is_mechanic(user):
            return qs.filter(mechanic_id=uid)
        if user_is_owner(user):
            return qs.filter(car__owner_id=uid)
        return MaintenanceRecord.objects.none()


class RecordListView(_RecordScopeMixin, BaseListAPIView):
    serializer_class = MaintenanceRecordSerializer
    list_success_message = "Maintenance records fetched successfully"


class RecordGetView(_RecordScopeMixin, BaseGetAPIView):
    serializer_class = MaintenanceRecordSerializer
    get_success_message = "Maintenance record fetched successfully"


class RecordCreateView(_RecordScopeMixin, BaseCreateAPIView):
    serializer_class = MaintenanceRecordSerializer
    create_success_message = "Maintenance record created successfully"


class RecordUpdateView(_RecordScopeMixin, BaseUpdateAPIView):
    serializer_class = MaintenanceRecordSerializer
    update_success_message = "Maintenance record updated successfully"


class RecordDeleteView(_RecordScopeMixin, BaseDeleteAPIView):
    serializer_class = MaintenanceRecordSerializer
    delete_success_message = "Maintenance record deleted successfully"
