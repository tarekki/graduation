from django.contrib import admin

from .models import CarBrand, CarColor, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(CarColor)
class CarColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
