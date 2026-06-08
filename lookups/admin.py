from django.contrib import admin

from .models import CarBrand, CarColor, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "name_ar")
    search_fields = ("code", "name", "name_ar")


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_ar")
    search_fields = ("name", "name_ar")


@admin.register(CarColor)
class CarColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_ar")
    search_fields = ("name", "name_ar")
