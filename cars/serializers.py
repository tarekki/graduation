from datetime import date

from rest_framework import serializers

from lookups.models import CarBrand, CarColor
from lookups.serializers import BrandMiniSerializer, ColorMiniSerializer, UserMiniSerializer

from .models import Car


class CarSerializer(serializers.ModelSerializer):
    """
    Read: nested `brand`, `color`, `owner` objects (id + name/name fields).
    Write: `brandId`, `colorId` accepted in the body. `owner` is auto-assigned.
    """

    brand_id = serializers.PrimaryKeyRelatedField(
        source="brand",
        queryset=CarBrand.objects.all(),
        write_only=True,
        error_messages={"does_not_exist": "Invalid brandId.", "incorrect_type": "brandId must be an integer."},
    )
    color_id = serializers.PrimaryKeyRelatedField(
        source="color",
        queryset=CarColor.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
        error_messages={"does_not_exist": "Invalid colorId.", "incorrect_type": "colorId must be an integer."},
    )

    brand = BrandMiniSerializer(read_only=True)
    color = ColorMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)

    class Meta:
        model = Car
        fields = (
            "id",
            "owner",
            "brand_id",
            "brand",
            "color_id",
            "color",
            "model",
            "year",
            "plate_number",
            "mileage",
            "created_at",
        )
        read_only_fields = ("id", "owner", "brand", "color", "created_at")

    def validate_model(self, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Model is required.")
        return text[:100]

    def validate_year(self, value: int) -> int:
        current = date.today().year
        if value < 1900:
            raise serializers.ValidationError("Year must be 1900 or later.")
        if value > current + 1:
            raise serializers.ValidationError(f"Year cannot be greater than {current + 1}.")
        return value

    def validate_plate_number(self, value: str) -> str:
        text = (value or "").strip().upper()
        if not text:
            raise serializers.ValidationError("Plate number is required.")
        return text[:30]

    def validate_mileage(self, value: int) -> int:
        if value > 2_000_000:
            raise serializers.ValidationError("Mileage value is unrealistically high.")
        return value
