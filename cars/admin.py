from django.contrib import admin

from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "model", "owner", "plate_number", "year", "mileage")
    list_select_related = ("owner", "brand", "color")
    search_fields = (
        "brand__name",
        "model",
        "plate_number",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
    )
    list_filter = ("brand", "year", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("owner", "brand", "model", "year", "plate_number")}),
        ("Details", {"fields": ("color", "mileage", "created_at")}),
    )
