from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from django.shortcuts import render

from apps.catalogos.models import Marca
from apps.inventario.models import Pieza, Vehiculo
from apps.yonkes.models import Yonke


def _safe_count(queryset, fallback=0):
    try:
        return queryset.count()
    except (OperationalError, ProgrammingError):
        return fallback


def _safe_piezas():
    try:
        return list(
            Pieza.objects.select_related("yonke")
            .only("id", "nombre", "estatus", "precio", "creado_en", "yonke__nombre")
            .order_by("-creado_en", "-id")[:5]
        )
    except (OperationalError, ProgrammingError):
        return []


def index(request):
    # TODO: Reemplazar por métrica real cuando exista tracking de búsquedas.
    busquedas_hoy = 0

    yonkes_activos = _safe_count(Yonke.objects.filter(estatus="activo"))
    if yonkes_activos == 0:
        yonkes_activos = _safe_count(Yonke.objects.all())

    vehiculos_registrados = _safe_count(Vehiculo.objects.all())
    piezas_disponibles = _safe_count(Pieza.objects.filter(Q(estatus="disponible") & Q(cantidad__gt=0)))

    ultimas_piezas = _safe_piezas()

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
