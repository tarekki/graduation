"""Shared serializers for POST-body payloads."""
from __future__ import annotations

from rest_framework import serializers


class IdPayloadSerializer(serializers.Serializer):
    """Validates {"id": <int>} coming from the request body."""

    id = serializers.IntegerField(min_value=1)
