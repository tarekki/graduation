from django.urls import path

from .views import (
    CarCreateView,
    CarDeleteView,
    CarGetView,
    CarListView,
    CarUpdateView,
)

urlpatterns = [
    path("list/", CarListView.as_view(), name="car-list"),
    path("get/", CarGetView.as_view(), name="car-get"),
    path("create/", CarCreateView.as_view(), name="car-create"),
    path("update/", CarUpdateView.as_view(), name="car-update"),
    path("delete/", CarDeleteView.as_view(), name="car-delete"),
]
