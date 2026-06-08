from common.views import BaseSimpleListAPIView

from .models import CarBrand, CarColor, Role
from .serializers import BrandMiniSerializer, ColorMiniSerializer, RoleMiniSerializer


class RoleListView(BaseSimpleListAPIView):
    """POST /api/lookups/roles/list/ → all roles (unpaginated)."""

    serializer_class = RoleMiniSerializer
    list_success_message = "Roles fetched successfully"

    def get_queryset(self):
        return Role.objects.all().order_by("code")


class CarBrandListView(BaseSimpleListAPIView):
    """POST /api/lookups/brands/list/ → all brands (unpaginated)."""

    serializer_class = BrandMiniSerializer
    list_success_message = "Brands fetched successfully"

    def get_queryset(self):
        return CarBrand.objects.all().order_by("name")


class CarColorListView(BaseSimpleListAPIView):
    """POST /api/lookups/colors/list/ → all colors (unpaginated)."""

    serializer_class = ColorMiniSerializer
    list_success_message = "Colors fetched successfully"

    def get_queryset(self):
        return CarColor.objects.all().order_by("name")
