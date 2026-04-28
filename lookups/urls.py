from django.urls import path

from .views import CarBrandListView, CarColorListView, RoleListView

urlpatterns = [
    path("roles/list/", RoleListView.as_view(), name="lookup-roles-list"),
    path("brands/list/", CarBrandListView.as_view(), name="lookup-brands-list"),
    path("colors/list/", CarColorListView.as_view(), name="lookup-colors-list"),
]
