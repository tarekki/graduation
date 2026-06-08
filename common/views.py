"""
Base POST-only API views.

All endpoints use POST (list/get/create/update/delete). IDs always travel in
the JSON body, never in the URL or query params.

Subclass `BaseListAPIView`, `BaseGetAPIView`, `BaseCreateAPIView`,
`BaseUpdateAPIView`, `BaseDeleteAPIView` and supply `serializer_class` plus
`get_queryset()`. The views return the standard {result, data, message} envelope.
"""
from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .pagination import paginate
from .responses import success_response
from .serializers import IdPayloadSerializer


class BasePostAPIView(APIView):
    """Common base for every endpoint.

    Defaults:
        http_method_names     = ["post"]
        authentication_classes = [JWTAuthentication]
        permission_classes     = [IsAuthenticated]

    Override in subclasses when the endpoint must be public or use a different
    permission policy, e.g.:

        class PublicListView(BaseListAPIView):
            authentication_classes = []
            permission_classes = [AllowAny]

        class OwnerOnlyView(BaseGetAPIView):
            permission_classes = [IsAuthenticated, IsOwnerOfResource]
    """

    http_method_names = ["post"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = None

    def get_serializer_class(self):
        assert self.serializer_class, f"{self.__class__.__name__} needs serializer_class"
        return self.serializer_class

    def get_serializer_context(self) -> dict[str, Any]:
        return {"request": self.request, "view": self}

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        return self.get_serializer_class()(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        raise NotImplementedError


class BaseListAPIView(BasePostAPIView):
    """POST /<resource>/list/ → paginated list in the standard envelope."""

    list_success_message = "Fetched successfully"

    def post(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        result = paginate(queryset, request.data or {})
        serializer = self.get_serializer(result.items, many=True)
        return success_response(
            data=result.to_dict(serializer.data),
            message=self.list_success_message,
        )


class BaseSimpleListAPIView(BasePostAPIView):
    """POST /<resource>/list/ → full, unpaginated list.

    For small, bounded sets (e.g. lookups) where pagination adds no value:
    `data` is the flat array of items, with no page/pageSize metadata.
    """

    list_success_message = "Fetched successfully"

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(
            data=serializer.data,
            message=self.list_success_message,
        )


class BaseSimpleListAPIView(BasePostAPIView):
    """POST /<resource>/list/ → full, unpaginated list in the standard envelope.

    `data` is a flat array of items. Use for small, bounded sets (e.g. lookups)
    where pagination adds no value; prefer `BaseListAPIView` for large datasets.
    """

    list_success_message = "Fetched successfully"

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(
            data=serializer.data,
            message=self.list_success_message,
        )


class _ObjectByIdMixin:
    """Shared helper: parse `id` from body and fetch from queryset."""

    def _get_object_from_body(self):
        payload = IdPayloadSerializer(data=self.request.data or {})
        payload.is_valid(raise_exception=True)
        obj_id = payload.validated_data["id"]
        from rest_framework.exceptions import NotFound

        obj = self.get_queryset().filter(pk=obj_id).first()
        if obj is None:
            raise NotFound("Resource not found")
        self.check_object_permissions(self.request, obj)
        return obj


class BaseGetAPIView(_ObjectByIdMixin, BasePostAPIView):
    """POST /<resource>/get/ with body {"id": <n>}."""

    get_success_message = "Fetched successfully"

    def post(self, request, *args, **kwargs) -> Response:
        obj = self._get_object_from_body()
        serializer = self.get_serializer(obj)
        return success_response(data=serializer.data, message=self.get_success_message)


class BaseCreateAPIView(BasePostAPIView):
    """POST /<resource>/create/ with the resource fields in the body."""

    create_success_message = "Created successfully"

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message=self.create_success_message,
            status_code=201,
        )

    def perform_create(self, serializer):
        serializer.save()


class BaseUpdateAPIView(_ObjectByIdMixin, BasePostAPIView):
    """POST /<resource>/update/ with body {"id": <n>, ...fields}."""

    update_success_message = "Updated successfully"
    partial = True

    def post(self, request, *args, **kwargs) -> Response:
        obj = self._get_object_from_body()
        data = {k: v for k, v in (request.data or {}).items() if k != "id"}
        serializer = self.get_serializer(instance=obj, data=data, partial=self.partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message=self.update_success_message)

    def perform_update(self, serializer):
        serializer.save()


class BaseDeleteAPIView(_ObjectByIdMixin, BasePostAPIView):
    """POST /<resource>/delete/ with body {"id": <n>}."""

    delete_success_message = "Deleted successfully"

    def post(self, request, *args, **kwargs) -> Response:
        obj = self._get_object_from_body()
        deleted_id = obj.pk
        self.perform_destroy(obj)
        return success_response(data={"id": deleted_id}, message=self.delete_success_message)

    def perform_destroy(self, instance):
        instance.delete()
