from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from django.contrib.auth import get_user_model
from apps.yonkes.models import Yonke
from apps.accounts.permissions import require_admin_area

from .models import AuditLog

User = get_user_model()


@require_admin_area
def auditoria_list(request):
    q = request.GET.get("q", "").strip()
    usuario = request.GET.get("usuario", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    accion = request.GET.get("accion", "").strip()
    entidad = request.GET.get("entidad", "").strip()
    fecha_desde = request.GET.get("fecha_desde", "").strip()
    fecha_hasta = request.GET.get("fecha_hasta", "").strip()

    logs = AuditLog.objects.select_related("usuario", "yonke").order_by("-creado_en", "-id")

    if q:
        logs = logs.filter(
            Q(entidad__icontains=q)
            | Q(accion__icontains=q)
            | Q(ip_address__icontains=q)
            | Q(user_agent__icontains=q)
            | Q(entidad_id__icontains=q)
        )
    if usuario:
        logs = logs.filter(usuario_id=usuario)
    if yonke:
        logs = logs.filter(yonke_id=yonke)
    if accion:
        logs = logs.filter(accion__icontains=accion)
    if entidad:
        logs = logs.filter(entidad__icontains=entidad)
    if fecha_desde:
        logs = logs.filter(creado_en__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(creado_en__date__lte=fecha_hasta)

    return render(
        request,
        "auditoria/list.html",
        {
            "active_module": "auditoria",
            "logs": logs,
            "usuarios": User.objects.all().order_by("username"),
            "yonkes": Yonke.objects.all().order_by("nombre"),
            "filters": {
                "q": q,
                "usuario": usuario,
                "yonke": yonke,
                "accion": accion,
                "entidad": entidad,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
            },
        },
    )


@require_admin_area
def auditoria_detail(request, pk):
    log = get_object_or_404(AuditLog.objects.select_related("usuario", "yonke"), pk=pk)
    return render(
        request,
        "auditoria/detail.html",
        {
            "active_module": "auditoria",
            "log": log,
        },
    )
