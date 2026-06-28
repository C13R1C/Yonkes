from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import (
    can_create_inventory,
    can_edit_inventory,
    can_view_sensitive_inventory,
    inventory_queryset_for_user,
    is_admin_general,
    own_yonke_queryset_for_user,
    user_yonke,
    yonkes_queryset_for_user,
)
from apps.auditoria.services import log_action
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


def _inventory_changes(before, after, fields):
    changes = {}
    for field in fields:
        old = getattr(before, field)
        new = getattr(after, field)
        if old != new:
            changes[field] = {"antes": str(old), "despues": str(new)}
    return changes


@login_required(login_url="/login/")
def vehiculo_list(request):
    queryset = inventory_queryset_for_user(
        Vehiculo.objects.select_related("yonke", "marca", "modelo").order_by("-creado_en", "-id"),
        request.user,
    )

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
        search_query = (
            Q(marca__nombre__icontains=q)
            | Q(modelo__nombre__icontains=q)
            | Q(marca_texto__icontains=q)
            | Q(modelo_texto__icontains=q)
            | Q(version__icontains=q)
            | Q(motor__icontains=q)
            | Q(transmision__icontains=q)
        )
        if is_admin_general(request.user):
            search_query |= Q(vin__icontains=q) | Q(numero_serie__icontains=q) | Q(ubicacion_fisica__icontains=q)
        queryset = queryset.filter(search_query)
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

    current_yonke = user_yonke(request.user)
    if current_yonke and not is_admin_general(request.user):
        queryset = queryset.annotate(
            prioridad_yonke=Case(
                When(yonke=current_yonke, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("prioridad_yonke", "-creado_en", "-id")
    else:
        queryset = queryset.annotate(prioridad_yonke=Value(0, output_field=IntegerField())).order_by("-creado_en", "-id")

    vehiculos = list(queryset)
    for vehiculo_obj in vehiculos:
        vehiculo_obj.can_edit = can_edit_inventory(request.user, vehiculo_obj)
        vehiculo_obj.can_view_sensitive = can_view_sensitive_inventory(request.user, vehiculo_obj)

    return render(
        request,
        "vehiculos/list.html",
        {
            "active_module": "vehiculos",
            "vehiculos": vehiculos,
            "can_create_inventory": can_create_inventory(request.user),
            "yonkes": yonkes_queryset_for_user(Yonke.objects.all().order_by("nombre"), request.user),
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


@login_required(login_url="/login/")
def vehiculo_detail(request, pk):
    vehiculo = get_object_or_404(
        inventory_queryset_for_user(Vehiculo.objects.select_related("yonke", "marca", "modelo"), request.user),
        pk=pk,
    )
    piezas = inventory_queryset_for_user(
        vehiculo.piezas.select_related("yonke", "categoria", "nombre_normalizado").order_by("-creado_en", "-id"),
        request.user,
    )
    piezas = list(piezas)
    for pieza_obj in piezas:
        pieza_obj.can_edit = can_edit_inventory(request.user, pieza_obj)
        pieza_obj.can_view_sensitive = can_view_sensitive_inventory(request.user, pieza_obj)
    return render(
        request,
        "vehiculos/detail.html",
        {
            "active_module": "vehiculos",
            "vehiculo": vehiculo,
            "vehiculo_label": _vehiculo_label(vehiculo),
            "piezas_count": vehiculo.piezas.count() if hasattr(vehiculo, "piezas") else None,
            "piezas": piezas,
            "can_edit": can_edit_inventory(request.user, vehiculo),
            "can_add_piece": can_create_inventory(request.user) and can_edit_inventory(request.user, vehiculo),
            "can_view_sensitive": can_view_sensitive_inventory(request.user, vehiculo),
        },
    )


@login_required(login_url="/login/")
def vehiculo_create(request):
    if not can_create_inventory(request.user):
        raise PermissionDenied
    form = VehiculoForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        vehiculo = form.save(commit=False)
        vehiculo.creado_por = request.user
        if not vehiculo.yonke_id:
            vehiculo.yonke = user_yonke(request.user)
        vehiculo.save()
        form.save_m2m()
        log_action(request, accion="crear_vehiculo", entidad="Vehiculo", entidad_id=vehiculo.pk, yonke=vehiculo.yonke)
        messages.success(request, "Registro creado correctamente.")
        return redirect("inventario_html:vehiculos-detail", pk=vehiculo.pk)
    return render(request, "vehiculos/form.html", {"active_module": "vehiculos", "form": form, "is_edit": False})


@login_required(login_url="/login/")
def vehiculo_edit(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if not can_edit_inventory(request.user, vehiculo):
        raise PermissionDenied
    before = Vehiculo.objects.get(pk=pk)
    form = VehiculoForm(request.POST or None, request.FILES or None, instance=vehiculo, user=request.user)
    if request.method == "POST" and form.is_valid():
        vehiculo = form.save()
        changes = _inventory_changes(before, vehiculo, ["estatus", "visibilidad"])
        log_action(request, accion="editar_vehiculo", entidad="Vehiculo", entidad_id=vehiculo.pk, yonke=vehiculo.yonke, cambios=changes)
        messages.success(request, "Registro actualizado correctamente.")
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


@login_required(login_url="/login/")
def pieza_list(request):
    queryset = inventory_queryset_for_user(
        Pieza.objects.select_related(
            "yonke", "vehiculo", "vehiculo__marca", "vehiculo__modelo", "categoria", "nombre_normalizado"
        ).order_by("-creado_en", "-id"),
        request.user,
    )

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
        search_query = (
            Q(nombre__icontains=q)
            | Q(nombre_normalizado__nombre_normalizado__icontains=q)
            | Q(alias_local__icontains=q)
        )
        if is_admin_general(request.user):
            search_query |= Q(ubicacion__icontains=q) | Q(observaciones__icontains=q)
        queryset = queryset.filter(search_query)
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

    current_yonke = user_yonke(request.user)
    if current_yonke and not is_admin_general(request.user):
        queryset = queryset.annotate(
            prioridad_yonke=Case(
                When(yonke=current_yonke, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("prioridad_yonke", "-creado_en", "-id")
    else:
        queryset = queryset.annotate(prioridad_yonke=Value(0, output_field=IntegerField())).order_by("-creado_en", "-id")

    piezas = list(queryset)
    for pieza_obj in piezas:
        pieza_obj.can_edit = can_edit_inventory(request.user, pieza_obj)
        pieza_obj.can_view_sensitive = can_view_sensitive_inventory(request.user, pieza_obj)

    return render(
        request,
        "piezas/list.html",
        {
            "active_module": "piezas",
            "piezas": piezas,
            "can_create_inventory": can_create_inventory(request.user),
            "yonkes": yonkes_queryset_for_user(Yonke.objects.all().order_by("nombre"), request.user),
            "vehiculos": own_yonke_queryset_for_user(Vehiculo.objects.select_related("marca", "modelo").order_by("-creado_en"), request.user)[:500],
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


@login_required(login_url="/login/")
def pieza_detail(request, pk):
    pieza = get_object_or_404(
        inventory_queryset_for_user(
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
            request.user,
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
            "can_edit": can_edit_inventory(request.user, pieza),
            "can_view_sensitive": can_view_sensitive_inventory(request.user, pieza),
        },
    )


@login_required(login_url="/login/")
def pieza_create(request):
    if not can_create_inventory(request.user):
        raise PermissionDenied
    vehiculo_context_id = request.GET.get("vehiculo") or request.POST.get("vehiculo_context")
    vehiculo_context = None
    initial = {}
    if vehiculo_context_id:
        vehiculo_context = get_object_or_404(Vehiculo.objects.select_related("yonke"), pk=vehiculo_context_id)
        if not can_edit_inventory(request.user, vehiculo_context):
            raise PermissionDenied
        initial = {"vehiculo": vehiculo_context, "yonke": vehiculo_context.yonke}

    form = PiezaForm(request.POST or None, request.FILES or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        pieza = form.save(commit=False)
        pieza.creado_por = request.user
        if vehiculo_context:
            pieza.vehiculo = vehiculo_context
            pieza.yonke = vehiculo_context.yonke
        if not pieza.yonke_id:
            pieza.yonke = user_yonke(request.user)
        pieza.save()
        form.save_m2m()
        log_action(request, accion="crear_pieza", entidad="Pieza", entidad_id=pieza.pk, yonke=pieza.yonke)
        messages.success(request, "Registro creado correctamente.")
        if vehiculo_context:
            return redirect("inventario_html:vehiculos-detail", pk=vehiculo_context.pk)
        return redirect("inventario_html:piezas-detail", pk=pieza.pk)
    return render(
        request,
        "piezas/form.html",
        {"active_module": "piezas", "form": form, "is_edit": False, "vehiculo_context": vehiculo_context},
    )


@login_required(login_url="/login/")
def pieza_edit(request, pk):
    pieza = get_object_or_404(Pieza, pk=pk)
    if not can_edit_inventory(request.user, pieza):
        raise PermissionDenied
    before = Pieza.objects.get(pk=pk)
    form = PiezaForm(request.POST or None, request.FILES or None, instance=pieza, user=request.user)
    if request.method == "POST" and form.is_valid():
        pieza = form.save()
        changes = _inventory_changes(before, pieza, ["estatus", "visibilidad", "precio", "precio_visible"])
        log_action(request, accion="editar_pieza", entidad="Pieza", entidad_id=pieza.pk, yonke=pieza.yonke, cambios=changes)
        messages.success(request, "Registro actualizado correctamente.")
        return redirect("inventario_html:piezas-detail", pk=pieza.pk)
    return render(
        request,
        "piezas/form.html",
        {"active_module": "piezas", "form": form, "is_edit": True, "pieza": pieza},
    )
