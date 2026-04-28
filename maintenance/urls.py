from django.urls import path

from .views import (
    AppointmentCreateView,
    AppointmentDeleteView,
    AppointmentGetView,
    AppointmentListView,
    AppointmentUpdateView,
    MileageLogCreateView,
    MileageLogDeleteView,
    MileageLogGetView,
    MileageLogListView,
    MileageLogUpdateView,
    RecordCreateView,
    RecordDeleteView,
    RecordGetView,
    RecordListView,
    RecordUpdateView,
    ReminderCreateView,
    ReminderDeleteView,
    ReminderGetView,
    ReminderListView,
    ReminderUpdateView,
)


def _crud(prefix: str, views: dict) -> list:
    return [
        path(f"{prefix}/list/", views["list"].as_view(), name=f"{prefix}-list"),
        path(f"{prefix}/get/", views["get"].as_view(), name=f"{prefix}-get"),
        path(f"{prefix}/create/", views["create"].as_view(), name=f"{prefix}-create"),
        path(f"{prefix}/update/", views["update"].as_view(), name=f"{prefix}-update"),
        path(f"{prefix}/delete/", views["delete"].as_view(), name=f"{prefix}-delete"),
    ]


urlpatterns = [
    *_crud(
        "mileage-logs",
        {
            "list": MileageLogListView,
            "get": MileageLogGetView,
            "create": MileageLogCreateView,
            "update": MileageLogUpdateView,
            "delete": MileageLogDeleteView,
        },
    ),
    *_crud(
        "reminders",
        {
            "list": ReminderListView,
            "get": ReminderGetView,
            "create": ReminderCreateView,
            "update": ReminderUpdateView,
            "delete": ReminderDeleteView,
        },
    ),
    *_crud(
        "appointments",
        {
            "list": AppointmentListView,
            "get": AppointmentGetView,
            "create": AppointmentCreateView,
            "update": AppointmentUpdateView,
            "delete": AppointmentDeleteView,
        },
    ),
    *_crud(
        "records",
        {
            "list": RecordListView,
            "get": RecordGetView,
            "create": RecordCreateView,
            "update": RecordUpdateView,
            "delete": RecordDeleteView,
        },
    ),
]
