from .models import AuditLog


def log_action(request, *, accion, entidad, entidad_id="", yonke=None, cambios=None):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        user = None
    meta = getattr(request, "META", {})
    x_forwarded_for = meta.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else meta.get("REMOTE_ADDR")
    return AuditLog.objects.create(
        usuario=user,
        yonke=yonke,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id or ""),
        cambios=cambios or {},
        ip_address=ip_address or None,
        user_agent=meta.get("HTTP_USER_AGENT", ""),
    )
