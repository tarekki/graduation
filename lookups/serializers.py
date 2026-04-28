"""
Lookup serializers.

Mini serializers (`*MiniSerializer`) expose `{id, name}` (+ code for Role) and are
the shared representation for any nested lookup in other modules' read payloads.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CarBrand, CarColor, Role

User = get_user_model()


class RoleMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "code", "name")


class BrandMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ("id", "name")


class ColorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarColor
        fields = ("id", "name")


class UserMiniSerializer(serializers.ModelSerializer):
    """Nested user: id + firstName + lastName (never exposes email/role/phone)."""

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
