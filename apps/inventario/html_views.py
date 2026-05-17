from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalogos.models import CategoriaPieza, Marca, ModeloVehiculo
from apps.yonkes.models import Yonke

from .forms import PiezaForm, VehiculoForm
from .models import Pieza, Vehiculo


def _vehiculo_label(vehiculo):
    marca = vehiculo.marca_texto or (vehiculo.marca.nombre if vehiculo.marca else "")
    modelo = vehiculo.modelo_texto or (vehiculo.modelo.nombre if vehiculo.modelo else "")
    anio = vehiculo.anio or ""
    return f"{marca} {modelo} {anio}".strip() or f"Vehículo {vehiculo.pk}"


def _pieza_vehiculo_label(pieza):
    if not pieza.vehiculo:
        return "—"
    return _vehiculo_label(pieza.vehiculo)


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
        return redirect("inventario_html:vehiculos-detail", pk=vehiculo.pk)
    return render(request, "vehiculos/form.html", {"active_module": "vehiculos", "form": form, "is_edit": False})


def vehiculo_edit(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, instance=vehiculo)
    if request.method == "POST" and form.is_valid():
        vehiculo = form.save()
        return redirect("inventario_html:vehiculos-detail", pk=vehiculo.pk)
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


def pieza_list(request):
    queryset = Pieza.objects.select_related(
        "yonke", "vehiculo", "vehiculo__marca", "vehiculo__modelo", "categoria", "nombre_normalizado"
    ).order_by("-creado_en", "-id")

    q = request.GET.get("q", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    vehiculo = request.GET.get("vehiculo", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    condicion = request.GET.get("condicion", "").strip()
    estatus = request.GET.get("estatus", "").strip()
    visibilidad = request.GET.get("visibilidad", "").strip()
    precio_min = request.GET.get("precio_min", "").strip()
    precio_max = request.GET.get("precio_max", "").strip()
    anio = request.GET.get("anio", "").strip()

    if q:
        queryset = queryset.filter(
            Q(nombre__icontains=q)
            | Q(nombre_normalizado__nombre_normalizado__icontains=q)
            | Q(alias_local__icontains=q)
            | Q(ubicacion__icontains=q)
            | Q(observaciones__icontains=q)
        )
    if yonke:
        queryset = queryset.filter(yonke_id=yonke)
    if vehiculo:
        queryset = queryset.filter(vehiculo_id=vehiculo)
    if categoria:
        queryset = queryset.filter(categoria_id=categoria)
    if condicion:
        queryset = queryset.filter(condicion=condicion)
    if estatus:
        queryset = queryset.filter(estatus=estatus)
    if visibilidad:
        queryset = queryset.filter(visibilidad=visibilidad)
    if precio_min:
        queryset = queryset.filter(precio__gte=precio_min)
    if precio_max:
        queryset = queryset.filter(precio__lte=precio_max)
    if anio:
        queryset = queryset.filter(Q(anio_inicio__lte=anio) & (Q(anio_fin__gte=anio) | Q(anio_fin__isnull=True)))

    return render(
        request,
        "piezas/list.html",
        {
            "active_module": "piezas",
            "piezas": queryset,
            "yonkes": Yonke.objects.all().order_by("nombre"),
            "vehiculos": Vehiculo.objects.select_related("marca", "modelo").order_by("-creado_en")[:500],
            "categorias": CategoriaPieza.objects.filter(activo=True).order_by("nombre"),
            "condicion_choices": Pieza.CONDICION_CHOICES,
            "estatus_choices": Pieza.ESTATUS_CHOICES,
            "visibilidad_choices": Pieza.VISIBILIDAD_CHOICES,
            "filters": {
                "q": q,
                "yonke": yonke,
                "vehiculo": vehiculo,
                "categoria": categoria,
                "condicion": condicion,
                "estatus": estatus,
                "visibilidad": visibilidad,
                "precio_min": precio_min,
                "precio_max": precio_max,
                "anio": anio,
            },
        },
    )


def pieza_detail(request, pk):
    pieza = get_object_or_404(
        Pieza.objects.select_related(
            "yonke",
            "vehiculo",
            "vehiculo__marca",
            "vehiculo__modelo",
            "categoria",
            "nombre_normalizado",
            "marca_compatible",
            "modelo_compatible",
        ),
        pk=pk,
    )
    return render(
        request,
        "piezas/detail.html",
        {
            "active_module": "piezas",
            "pieza": pieza,
            "vehiculo_label": _pieza_vehiculo_label(pieza),
        },
    )


def pieza_create(request):
    form = PiezaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pieza = form.save()
        return redirect("inventario_html:piezas-detail", pk=pieza.pk)
    return render(request, "piezas/form.html", {"active_module": "piezas", "form": form, "is_edit": False})


def pieza_edit(request, pk):
    pieza = get_object_or_404(Pieza, pk=pk)
    form = PiezaForm(request.POST or None, instance=pieza)
    if request.method == "POST" and form.is_valid():
        pieza = form.save()
        return redirect("inventario_html:piezas-detail", pk=pieza.pk)
    return render(
        request,
        "piezas/form.html",
        {"active_module": "piezas", "form": form, "is_edit": True, "pieza": pieza},
    )
