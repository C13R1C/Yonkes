from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalogos.models import Marca, ModeloVehiculo
from apps.yonkes.models import Yonke

from .forms import VehiculoForm
from .models import Vehiculo


def _vehiculo_label(vehiculo):
    marca = vehiculo.marca_texto or (vehiculo.marca.nombre if vehiculo.marca else "")
    modelo = vehiculo.modelo_texto or (vehiculo.modelo.nombre if vehiculo.modelo else "")
    anio = vehiculo.anio or ""
    return f"{marca} {modelo} {anio}".strip() or f"Vehículo {vehiculo.pk}"


def vehiculo_list(request):
    queryset = Vehiculo.objects.select_related("yonke", "marca", "modelo").order_by("-creado_en", "-id")

    q = request.GET.get("q", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    marca = request.GET.get("marca", "").strip()
    modelo = request.GET.get("modelo", "").strip()
    anio = request.GET.get("anio", "").strip()
    anio_min = request.GET.get("anio_min", "").strip()
    anio_max = request.GET.get("anio_max", "").strip()
    estatus = request.GET.get("estatus", "").strip()
    visibilidad = request.GET.get("visibilidad", "").strip()

    if q:
        queryset = queryset.filter(
            Q(marca__nombre__icontains=q)
            | Q(modelo__nombre__icontains=q)
            | Q(marca_texto__icontains=q)
            | Q(modelo_texto__icontains=q)
            | Q(version__icontains=q)
            | Q(motor__icontains=q)
            | Q(transmision__icontains=q)
            | Q(vin__icontains=q)
            | Q(numero_serie__icontains=q)
            | Q(ubicacion_fisica__icontains=q)
        )
    if yonke:
        queryset = queryset.filter(yonke_id=yonke)
    if marca:
        queryset = queryset.filter(marca_id=marca)
    if modelo:
        queryset = queryset.filter(modelo_id=modelo)
    if anio:
        queryset = queryset.filter(anio=anio)
    if anio_min:
        queryset = queryset.filter(anio__gte=anio_min)
    if anio_max:
        queryset = queryset.filter(anio__lte=anio_max)
    if estatus:
        queryset = queryset.filter(estatus=estatus)
    if visibilidad:
        queryset = queryset.filter(visibilidad=visibilidad)

    return render(
        request,
        "vehiculos/list.html",
        {
            "active_module": "vehiculos",
            "vehiculos": queryset,
            "yonkes": Yonke.objects.all().order_by("nombre"),
            "marcas": Marca.objects.filter(activo=True).order_by("nombre"),
            "modelos": ModeloVehiculo.objects.filter(activo=True).select_related("marca").order_by("marca__nombre", "nombre"),
            "estatus_choices": Vehiculo.ESTATUS_CHOICES,
            "visibilidad_choices": Vehiculo.VISIBILIDAD_CHOICES,
            "filters": {
                "q": q,
                "yonke": yonke,
                "marca": marca,
                "modelo": modelo,
                "anio": anio,
                "anio_min": anio_min,
                "anio_max": anio_max,
                "estatus": estatus,
                "visibilidad": visibilidad,
            },
        },
    )


def vehiculo_detail(request, pk):
    vehiculo = get_object_or_404(Vehiculo.objects.select_related("yonke", "marca", "modelo"), pk=pk)
    return render(
        request,
        "vehiculos/detail.html",
        {
            "active_module": "vehiculos",
            "vehiculo": vehiculo,
            "vehiculo_label": _vehiculo_label(vehiculo),
            "piezas_count": vehiculo.piezas.count() if hasattr(vehiculo, "piezas") else None,
        },
    )


def vehiculo_create(request):
    form = VehiculoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        vehiculo = form.save()
        return redirect("vehiculos-detail", pk=vehiculo.pk)
    return render(request, "vehiculos/form.html", {"active_module": "vehiculos", "form": form, "is_edit": False})


def vehiculo_edit(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, instance=vehiculo)
    if request.method == "POST" and form.is_valid():
        vehiculo = form.save()
        return redirect("vehiculos-detail", pk=vehiculo.pk)
    return render(
        request,
        "vehiculos/form.html",
        {
            "active_module": "vehiculos",
            "form": form,
            "is_edit": True,
            "vehiculo": vehiculo,
            "vehiculo_label": _vehiculo_label(vehiculo),
        },
    )
