from common.views import BaseListAPIView

from .models import CarBrand, CarColor, Role
from .serializers import BrandMiniSerializer, ColorMiniSerializer, RoleMiniSerializer


class RoleListView(BaseListAPIView):
    """POST /api/lookups/roles/list/"""

    serializer_class = RoleMiniSerializer
    list_success_message = "Roles fetched successfully"

    def get_queryset(self):
        return Role.objects.all().order_by("code")


class CarBrandListView(BaseListAPIView):
    """POST /api/lookups/brands/list/"""

    serializer_class = BrandMiniSerializer
    list_success_message = "Brands fetched successfully"

    def get_queryset(self):
        return CarBrand.objects.all().order_by("name")


class CarColorListView(BaseListAPIView):
    """POST /api/lookups/colors/list/"""

    serializer_class = ColorMiniSerializer
    list_success_message = "Colors fetched successfully"

    def get_queryset(self):
        return CarColor.objects.all().order_by("name")
