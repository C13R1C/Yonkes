from .models import AuditLog

SENSITIVE_KEYS = {"password", "password_confirm", "token", "csrfmiddlewaretoken", "archivo", "file"}


def _sanitize(value):
    if isinstance(value, dict):
        return {key: ("[redacted]" if key.lower() in SENSITIVE_KEYS else _sanitize(val)) for key, val in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def log_action(request, *, accion, entidad, entidad_id="", yonke=None, cambios=None):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        user = None
    meta = getattr(request, "META", {})
    ip_address = meta.get("REMOTE_ADDR")
    try:
        return AuditLog.objects.create(
        usuario=user,
        yonke=yonke,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id or ""),
            cambios=_sanitize(cambios or {}),
            ip_address=ip_address or None,
            user_agent=meta.get("HTTP_USER_AGENT", ""),
        )
    except Exception:
        return None
