from django.urls import path
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    return JsonResponse({
        "success": True,
        "status": "ok",
        "database": db_status,
    })


urlpatterns = [
    path("", health_check, name="health-check"),
]