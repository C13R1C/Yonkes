from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import is_admin_general, is_dueno_yonke, is_empleado, user_yonke, user_yonke_is_active
from apps.yonkes.models import Yonke

from .forms import AliasPiezaForm, CategoriaPiezaForm, MarcaForm, ModeloVehiculoForm, NombrePiezaForm
from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza


CATALOG_CARDS = [
    ("marcas", "Marcas", "Marcas registradas por cada yonke.", Marca),
    ("modelos", "Modelos", "Modelos de vehículo vinculados a marcas del yonke.", ModeloVehiculo),
    ("categorias", "Categorías", "Clasificación principal de tipos de piezas.", CategoriaPieza),
    ("nombres-piezas", "Nombres de piezas", "Nombres normalizados de piezas del yonke.", NombrePieza),
    ("alias-piezas", "Alias de piezas", "Sinónimos y variantes de nombres de piezas.", AliasPieza),
]


def _is_catalog_operator(user):
    return is_dueno_yonke(user) or is_empleado(user)


def _can_access_catalogs(user):
    return is_admin_general(user) or _is_catalog_operator(user)


def _can_manage_catalogs(user):
    return _is_catalog_operator(user) and user_yonke_is_active(user)


def _require_catalog_access(request):
    if not _can_access_catalogs(request.user):
        messages.error(request, "No tienes permiso para realizar esta acción.")
        raise PermissionDenied


def _catalog_queryset(model, user, selected_yonke=""):
    qs = model.objects.all()
    if is_admin_general(user):
        if selected_yonke:
            qs = qs.filter(yonke_id=selected_yonke)
        return qs
    if _is_catalog_operator(user):
        return qs.filter(yonke=user_yonke(user))
    return qs.none()


def _owner_label(obj):
    return obj.yonke.nombre if getattr(obj, "yonke", None) else "Sin yonke asignado"


def _can_edit_row(user, obj):
    return _can_manage_catalogs(user) and getattr(obj, "yonke_id", None) == getattr(user_yonke(user), "pk", None)


@login_required(login_url="/login/")
def index(request):
    _require_catalog_access(request)
    cards = [
        {
            "slug": slug,
            "title": title,
            "description": description,
            "total": _catalog_queryset(model, request.user).count(),
        }
        for slug, title, description, model in CATALOG_CARDS
    ]
    return render(
        request,
        "catalogos/index.html",
        {
            "active_module": "catalogos",
            "cards": cards,
            "is_catalog_read_only": is_admin_general(request.user),
        },
    )


def _catalog_list(request, *, model, title, slug, q_fields):
    _require_catalog_access(request)
    selected_yonke = request.GET.get("yonke", "").strip()
    q = request.GET.get("q", "").strip()

    qs = _catalog_queryset(model, request.user, selected_yonke)
    if q:
        query = Q()
        for field in q_fields:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query)

    rows = list(qs)
    duplicate_keys = {}
    for row in rows:
        row.owner_label = _owner_label(row)
        row.can_edit_catalog = _can_edit_row(request.user, row)
        duplicate_key = str(row).strip().lower()
        duplicate_keys[duplicate_key] = duplicate_keys.get(duplicate_key, 0) + 1

    duplicate_count = 0
    for row in rows:
        row.is_duplicate_catalog = duplicate_keys.get(str(row).strip().lower(), 0) > 1
        if row.is_duplicate_catalog:
            duplicate_count += 1

    return render(
        request,
        "catalogos/list.html",
        {
            "active_module": "catalogos",
            "title": title,
            "slug": slug,
            "rows": rows,
            "q": q,
            "selected_yonke": selected_yonke,
            "yonkes": Yonke.objects.all().order_by("nombre") if is_admin_general(request.user) else Yonke.objects.filter(pk=getattr(user_yonke(request.user), "pk", None)),
            "can_create": _can_manage_catalogs(request.user),
            "is_catalog_read_only": is_admin_general(request.user),
            "total_registros": len(rows),
            "duplicate_count": duplicate_count,
        },
    )


def _catalog_form(request, *, model, form_class, slug, title, pk=None):
    _require_catalog_access(request)
    if not _can_manage_catalogs(request.user):
        messages.error(request, "No tienes permiso para realizar esta acción.")
        raise PermissionDenied

    queryset = _catalog_queryset(model, request.user)
    instance = get_object_or_404(queryset, pk=pk) if pk else None
    if instance and not _can_edit_row(request.user, instance):
        messages.error(request, "No tienes permiso para realizar esta acción.")
        raise PermissionDenied

    form = form_class(request.POST or None, request.FILES or None, instance=instance, user=request.user)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.yonke = user_yonke(request.user)
        obj.save()
        form.save_m2m()
        messages.success(request, "Registro actualizado correctamente." if pk else "Registro creado correctamente.")
        return redirect(f"catalogos-{slug}-list")

    return render(
        request,
        "catalogos/form.html",
        {
            "active_module": "catalogos",
            "title": title,
            "slug": slug,
            "form": form,
            "is_edit": bool(pk),
            "object": instance,
        },
    )


@login_required(login_url="/login/")
def marcas_list(request):
    return _catalog_list(request, model=Marca, title="Marcas", slug="marcas", q_fields=["nombre", "yonke__nombre"])


@login_required(login_url="/login/")
def marcas_create(request):
    return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca")


@login_required(login_url="/login/")
def marcas_edit(request, pk):
    return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca", pk=pk)


@login_required(login_url="/login/")
def modelos_list(request):
    return _catalog_list(request, model=ModeloVehiculo, title="Modelos", slug="modelos", q_fields=["nombre", "marca__nombre", "yonke__nombre"])


@login_required(login_url="/login/")
def modelos_create(request):
    return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo")


@login_required(login_url="/login/")
def modelos_edit(request, pk):
    return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo", pk=pk)


@login_required(login_url="/login/")
def categorias_list(request):
    return _catalog_list(request, model=CategoriaPieza, title="Categorías", slug="categorias", q_fields=["nombre", "yonke__nombre"])


@login_required(login_url="/login/")
def categorias_create(request):
    return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría")


@login_required(login_url="/login/")
def categorias_edit(request, pk):
    return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría", pk=pk)


@login_required(login_url="/login/")
def nombres_piezas_list(request):
    return _catalog_list(request, model=NombrePieza, title="Nombres de piezas", slug="nombres-piezas", q_fields=["nombre_normalizado", "categoria__nombre", "yonke__nombre"])


@login_required(login_url="/login/")
def nombres_piezas_create(request):
    return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza")


@login_required(login_url="/login/")
def nombres_piezas_edit(request, pk):
    return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza", pk=pk)


@login_required(login_url="/login/")
def alias_piezas_list(request):
    return _catalog_list(request, model=AliasPieza, title="Alias de piezas", slug="alias-piezas", q_fields=["alias", "nombre_pieza__nombre_normalizado", "yonke__nombre"])


@login_required(login_url="/login/")
def alias_piezas_create(request):
    return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza")


@login_required(login_url="/login/")
def alias_piezas_edit(request, pk):
    return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza", pk=pk)
