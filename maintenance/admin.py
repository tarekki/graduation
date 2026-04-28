from django.contrib import admin

from .models import (
    MaintenanceAppointment,
    MaintenanceRecord,
    MaintenanceReminder,
    MileageLog,
)


@admin.register(MileageLog)
class MileageLogAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "mileage", "recorded_at", "note_preview")
    list_select_related = ("car", "car__owner", "car__brand")
    search_fields = (
        "car__plate_number",
        "car__brand__name",
        "car__model",
        "note",
        "car__owner__email",
        "car__owner__first_name",
        "car__owner__last_name",
    )
    list_filter = ("recorded_at",)
    ordering = ("-recorded_at",)
    readonly_fields = ("recorded_at",)

    @admin.display(description="Note")
    def note_preview(self, obj):
        if not obj.note:
            return "—"
        return (obj.note[:60] + "…") if len(obj.note) > 60 else obj.note


@admin.register(MaintenanceReminder)
class MaintenanceReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "title", "due_date", "created_at")
    list_select_related = ("car", "car__owner", "car__brand")
    search_fields = ("title", "car__plate_number", "car__brand__name", "notes")
    list_filter = ("due_date", "created_at")
    ordering = ("due_date",)
    readonly_fields = ("created_at",)
    date_hierarchy = "due_date"


@admin.register(MaintenanceAppointment)
class MaintenanceAppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "car",
        "owner",
        "mechanic",
        "service_type",
        "appointment_date",
        "status",
        "created_at",
    )
    list_select_related = ("car", "owner", "mechanic")
    search_fields = (
        "car__plate_number",
        "car__brand__name",
        "car__model",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "mechanic__email",
        "mechanic__first_name",
        "mechanic__last_name",
        "service_type",
        "description",
    )
    list_filter = ("status", "appointment_date", "created_at")
    ordering = ("-appointment_date",)
    readonly_fields = ("created_at",)
    date_hierarchy = "appointment_date"


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "car",
        "appointment",
        "mechanic",
        "service_done",
        "cost",
        "service_date",
        "created_at",
    )
    list_select_related = ("car", "car__brand", "appointment", "mechanic")
    search_fields = (
        "car__model",
        "car__plate_number",
        "mechanic__email",
        "mechanic__first_name",
        "mechanic__last_name",
        "service_done",
    )
    list_filter = ("service_date", "created_at")
    ordering = ("-service_date", "-id")
    readonly_fields = ("created_at",)
    date_hierarchy = "service_date"
