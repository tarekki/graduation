"""
Public health-check endpoint for uptime probes, load balancers, and demos.

POST /api/health/ → 200, {status: "ok", database: "ok" | "error"}

Kept public (no auth) so ops tooling doesn't need credentials. A real DB
round-trip is run so "ok" means the API AND its primary DB are both up.
"""
from __future__ import annotations

import logging

from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .responses import success_response

logger = logging.getLogger("carnova.health")


class HealthCheckView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        db_status = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as exc:
            db_status = "error"
            logger.warning("Health check DB probe failed: %s", exc)

        return success_response(
            data={"status": "ok", "database": db_status},
            message="Service is healthy",
        )
