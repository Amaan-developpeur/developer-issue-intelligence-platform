from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from core.models import AuditLog
import json
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.warning("custom_exception_handler triggered for %s", exc)
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        request = context.get("request")
        user = getattr(request, "user", None)
        api_key = getattr(request, "api_key", None)

        payload = {
            "action": "throttle_violation",
            "path": request.path,
            "method": request.method,
            "ip": request.META.get("REMOTE_ADDR"),
            "remaining_wait_seconds": exc.wait,
            "auth_type": (
                "api_key"
                if api_key
                else "user" if user and user.is_authenticated
                else "anon"
            ),
        }

        try:
            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                endpoint=request.path,
                method=request.method,
                action="throttle_violation",
                result_status="429",
                payload=payload,  # let Django JSONField handle it directly
            )
        except Exception as e:
            logger.error("AuditLog insert failed: %s", e, exc_info=True)

    return response
