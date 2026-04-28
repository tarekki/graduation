from common.views import (
    BaseCreateAPIView,
    BaseDeleteAPIView,
    BaseGetAPIView,
    BaseListAPIView,
    BaseUpdateAPIView,
)

from .models import Car
from .permissions import user_is_admin
from .serializers import CarSerializer


class _CarScopedQuerysetMixin:
    """Shared queryset: admins see all cars; everyone else only their own."""

    def get_queryset(self):
        qs = (
            Car.objects
            .select_related("owner", "brand", "color")
            .order_by("-created_at", "-id")
        )
        user = self.request.user
        if user_is_admin(user):
            return qs
        return qs.filter(owner_id=user.pk)


class CarListView(_CarScopedQuerysetMixin, BaseListAPIView):
    """POST /api/cars/list/"""

    serializer_class = CarSerializer
    list_success_message = "Cars fetched successfully"


class CarGetView(_CarScopedQuerysetMixin, BaseGetAPIView):
    """POST /api/cars/get/ with body {"id": <n>}"""

    serializer_class = CarSerializer
    get_success_message = "Car fetched successfully"


class CarCreateView(_CarScopedQuerysetMixin, BaseCreateAPIView):
    """POST /api/cars/create/ — owner is always the logged-in user."""

    serializer_class = CarSerializer
    create_success_message = "Car created successfully"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CarUpdateView(_CarScopedQuerysetMixin, BaseUpdateAPIView):
    """POST /api/cars/update/ with body {"id": <n>, ...}"""

    serializer_class = CarSerializer
    update_success_message = "Car updated successfully"


class CarDeleteView(_CarScopedQuerysetMixin, BaseDeleteAPIView):
    """POST /api/cars/delete/ with body {"id": <n>}"""

    serializer_class = CarSerializer
    delete_success_message = "Car deleted successfully"
