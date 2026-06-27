from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from django.shortcuts import render

from apps.accounts.permissions import can_view_sensitive_inventory, inventory_queryset_for_user, is_admin_general, user_yonke
from apps.catalogos.models import Marca
from apps.inventario.models import Pieza, Vehiculo
from apps.yonkes.models import Yonke


def _safe_count(queryset, fallback=0):
    try:
        return queryset.count()
    except (OperationalError, ProgrammingError):
        return fallback


def _safe_piezas(user):
    try:
        piezas = list(
            inventory_queryset_for_user(Pieza.objects.select_related("yonke", "vehiculo"), user)
            .only(
                "id",
                "nombre",
                "estatus",
                "precio",
                "precio_visible",
                "imagen_principal",
                "creado_en",
                "yonke__nombre",
                "vehiculo__imagen_principal",
            )
            .order_by("-creado_en", "-id")[:5]
        )
        for pieza in piezas:
            pieza.can_view_sensitive = can_view_sensitive_inventory(user, pieza)
        return piezas
    except (OperationalError, ProgrammingError):
        return []


@login_required(login_url="/login/")
def index(request):
    # TODO: Reemplazar por métrica real cuando exista tracking de búsquedas.
    busquedas_hoy = 0

    yonkes_base = Yonke.objects.all() if is_admin_general(request.user) else Yonke.objects.filter(pk=getattr(user_yonke(request.user), "pk", None))
    yonkes_activos = _safe_count(yonkes_base.filter(estatus="activo"))
    if yonkes_activos == 0:
        yonkes_activos = _safe_count(yonkes_base)

    vehiculos_registrados = _safe_count(inventory_queryset_for_user(Vehiculo.objects.all(), request.user))
    piezas_disponibles = _safe_count(inventory_queryset_for_user(Pieza.objects.filter(Q(estatus="disponible") & Q(cantidad__gt=0)), request.user))

    ultimas_piezas = _safe_piezas(request.user)

    actividad_reciente = [
        {"title": "Nueva pieza registrada", "meta": "Hace 5 minutos"},
        {"title": "Vehículo actualizado", "meta": "Hace 22 minutos"},
        {"title": "Yonke activado", "meta": "Hace 1 hora"},
        {"title": "Precio modificado", "meta": "Hace 2 horas"},
    ]

    return render(
        request,
        "dashboard/index.html",
        {
            "active_module": "dashboard",
            "metrics": {
                "yonkes_activos": yonkes_activos,
                "vehiculos_registrados": vehiculos_registrados,
                "piezas_disponibles": piezas_disponibles,
                "busquedas_hoy": busquedas_hoy,
            },
            "ultimas_piezas": ultimas_piezas,
            "actividad_reciente": actividad_reciente,
            "marcas": Marca.objects.filter(activo=True).order_by("nombre"),
        },
    )


def module_placeholder(request, module_name, module_label):
    return render(
        request,
        "dashboard/module_placeholder.html",
        {
            "active_module": module_name,
            "module_name": module_name,
            "module_label": module_label,
        },
    )


def yonkes(request):
    return module_placeholder(request, "yonkes", "Yonkes")


def vehiculos(request):
    return module_placeholder(request, "vehiculos", "Vehículos")


def piezas(request):
    return module_placeholder(request, "piezas", "Piezas")


def busqueda(request):
    return module_placeholder(request, "busqueda", "Búsqueda")


def catalogos(request):
    return module_placeholder(request, "catalogos", "Catálogos")


def importaciones(request):
    return module_placeholder(request, "importaciones", "Importaciones")


def auditoria(request):
    return module_placeholder(request, "auditoria", "Auditoría")


def usuarios(request):
    return module_placeholder(request, "usuarios", "Usuarios")
