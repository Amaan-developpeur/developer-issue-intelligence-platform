# core/middleware.py
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from core.models import AuditLog, ApiKey

logger = logging.getLogger(__name__)

# Sensitive endpoints to audit
SENSITIVE_PREFIXES = ['/tasks/', '/metrics/', '/admin/']
# Common keys that must be redacted
SENSITIVE_KEYS = {
    "password", "passwd", "pass", "token", "refresh", "access",
    "authorization", "auth", "api_key", "secret"
}


def _sanitize_json(obj):
    """
    Walk the JSON-like structure (dict/list/primitive) and replace sensitive values.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = k.lower()
            if lk in SENSITIVE_KEYS or ("token" in lk) or ("secret" in lk):
                out[k] = "[REDACTED]"
            else:
                out[k] = _sanitize_json(v)
        return out
    if isinstance(obj, list):
        return [_sanitize_json(i) for i in obj]
    return obj  # primitive


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that logs sensitive endpoint activity, scrubbing secrets from payloads.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        path = getattr(request, "path", "")
        if not any(path.startswith(p) for p in SENSITIVE_PREFIXES):
            return None

        payload = None
        try:
            if request.content_type == "application/json":
                raw = request.body.decode("utf-8")[:2000]
                if raw:
                    try:
                        parsed = json.loads(raw)
                        payload = _sanitize_json(parsed)
                    except Exception:
                        # If invalid JSON, keep minimal safe snippet
                        snippet = raw
                        for s in SENSITIVE_KEYS:
                            snippet = snippet.replace(s, "[REDACTED]")
                        payload = {"raw": snippet[:1000]}
            else:
                payload = {"raw": f"{request.content_type} (not stored)"}
        except Exception as e:
            logger.debug("AuditMiddleware: failed to parse payload: %s", e)
            payload = None

        try:
            AuditLog.objects.create(
                user=None,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT"),
                endpoint=path,
                method=request.method,
                action="request",
                payload=payload,
                result_status=None,
            )
        except Exception as e:
            logger.error("AuditMiddleware: failed to create audit log: %s", e)

        return None

    def process_response(self, request, response):
        path = getattr(request, "path", "")
        if not path or not any(path.startswith(p) for p in SENSITIVE_PREFIXES):
            return response

        try:
            last_log = AuditLog.objects.filter(endpoint=path).order_by("-created_at").first()
            if last_log and last_log.result_status is None:
                last_log.result_status = str(response.status_code)
                if getattr(request, "user", None) and request.user.is_authenticated:
                    last_log.user = request.user
                last_log.save(update_fields=["result_status", "user"])
        except Exception as e:
            logger.error("AuditMiddleware: failed to update audit log: %s", e)

        return response


class ApiKeyAuthMiddleware(MiddlewareMixin):
    """
    Middleware that authenticates requests using an API key.
    Header: Authorization: ApiKey <token>
    """
    def process_request(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("ApiKey "):
            key_value = auth_header.split(" ", 1)[1].strip()
            try:
                api_key = ApiKey.objects.get(key=key_value, is_active=True)
                request.api_key = api_key
            except ApiKey.DoesNotExist:
                request.api_key = None
        else:
            request.api_key = None

    def process_response(self, request, response):
        path = getattr(request, "path", None)
        if path and any(path.startswith(p) for p in SENSITIVE_PREFIXES):
            last_log = AuditLog.objects.filter(endpoint=path).order_by("-created_at").first()
            if last_log and last_log.result_status is None:
                last_log.result_status = str(response.status_code)
                if getattr(request, "user", None) and request.user.is_authenticated:
                    last_log.user = request.user
                last_log.save(update_fields=["result_status", "user"])
        return response
