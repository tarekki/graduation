"""
Lookup serializers.

Mini serializers (`*MiniSerializer`) expose `{id, name}` (+ code for Role) and are
the shared representation for any nested lookup in other modules' read payloads.

`name` is localized from the request locale (see `common.locale.get_locale`):
Arabic requests get `name_ar` when set, otherwise the default English `name`.
Localization applies wherever these serializers are nested, since DRF shares the
parent serializer's request context with its children.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.locale import get_locale

from .models import CarBrand, CarColor, Role

User = get_user_model()


class LocalizedNameSerializer(serializers.ModelSerializer):
    """Resolves `name` to the Arabic label for Arabic requests (English fallback)."""

    name = serializers.SerializerMethodField()

    def get_name(self, obj) -> str:
        if get_locale(self.context.get("request")) == "ar":
            return getattr(obj, "name_ar", "") or obj.name
        return obj.name


class RoleMiniSerializer(LocalizedNameSerializer):
    class Meta:
        model = Role
        fields = ("id", "code", "name")


class BrandMiniSerializer(LocalizedNameSerializer):
    class Meta:
        model = CarBrand
        fields = ("id", "name")


class ColorMiniSerializer(LocalizedNameSerializer):
    class Meta:
        model = CarColor
        fields = ("id", "name")


class UserMiniSerializer(serializers.ModelSerializer):
    """Nested user: id + firstName + lastName (never exposes email/role/phone)."""

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
