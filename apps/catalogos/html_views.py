from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.permissions import is_admin_general, user_yonke
from apps.yonkes.models import Yonke

from .forms import AliasPiezaForm, CategoriaPiezaForm, MarcaForm, ModeloVehiculoForm, NombrePiezaForm
from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from .permissions import can_access_catalogs, can_manage_catalog_record, scope_catalog_queryset

CATALOGS = {
    "marcas": (Marca, MarcaForm, "Marcas", "Marca", ["nombre"]),
    "modelos": (ModeloVehiculo, ModeloVehiculoForm, "Modelos", "Modelo", ["nombre", "marca__nombre"]),
    "categorias": (CategoriaPieza, CategoriaPiezaForm, "Categorías", "Categoría", ["nombre"]),
    "nombres-piezas": (NombrePieza, NombrePiezaForm, "Nombres de piezas", "Nombre de pieza", ["nombre_normalizado", "categoria__nombre"]),
    "alias-piezas": (AliasPieza, AliasPiezaForm, "Alias de piezas", "Alias de pieza", ["alias", "nombre_pieza__nombre_normalizado"]),
}


def _ensure_catalog_access(request):
    if not can_access_catalogs(request.user):
        raise PermissionDenied("No tienes permiso para realizar esta acción.")


def _is_in_use(obj):
    for relation in obj._meta.related_objects:
        accessor = relation.get_accessor_name()
        if not accessor:
            continue
        manager = getattr(obj, accessor, None)
        if manager is not None and manager.exists():
            return True
    return False


def _safe_delete_or_deactivate(obj):
    if _is_in_use(obj):
        if hasattr(obj, "activo"):
            obj.activo = False
            obj.save(update_fields=["activo"])
            return "deactivated"
        return "blocked"
    obj.delete()
    return "deleted"

def _catalog_queryset(model, user, selected_yonke=""):
    return catalog_queryset_for_user(model.objects.all(), user, selected_yonke=selected_yonke, include_alias_shared=(model is not AliasPieza))


def _can_edit_row(user, obj):
    return can_edit_catalog_item(user, obj)


@login_required(login_url="/login/")
def index(request):
    _ensure_catalog_access(request)
    cards = []
    for slug, (model, _form, title, _singular, _q_fields) in CATALOGS.items():
        cards.append({"slug": slug, "title": title, "description": _description(slug), "total": scope_catalog_queryset(request.user, model.objects.all()).count()})
    return render(request, "catalogos/index.html", {"active_module": "catalogos", "cards": cards})


def _description(slug):
    return {
        "marcas": "Marcas base para vehículos y compatibilidad de piezas.",
        "modelos": "Modelos de vehículo vinculados a cada marca.",
        "categorias": "Clasificación principal de tipos de piezas.",
        "nombres-piezas": "Nombres normalizados para búsquedas y catálogo.",
        "alias-piezas": "Sinónimos y variantes de nombres de piezas.",
    }[slug]


def _catalog_list(request, *, model, title, slug, q_fields):
    _ensure_catalog_access(request)
    q = request.GET.get("q", "").strip()
    qs = scope_catalog_queryset(request.user, model.objects.all())
    if q:
        query = Q()
        for field in q_fields:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query)
    rows = list(qs)
    for row in rows:
        row.can_delete = can_manage_catalog_record(request.user, row)
    return render(request, "catalogos/list.html", {"active_module": "catalogos", "title": title, "slug": slug, "rows": rows, "q": q})


def _catalog_form(request, *, model, form_class, slug, title, pk=None):
    _ensure_catalog_access(request)
    instance = get_object_or_404(scope_catalog_queryset(request.user, model.objects.all()), pk=pk) if pk else None
    if instance and not can_manage_catalog_record(request.user, instance):
        raise PermissionDenied("No tienes permiso para realizar esta acción.")
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if not pk and hasattr(obj, "yonke_id"):
            profile = request.user.profile
            obj.yonke = None if profile.rol == profile.ROLE_ADMIN_GENERAL else profile.yonke
        if not can_manage_catalog_record(request.user, obj):
            raise PermissionDenied("No tienes permiso para realizar esta acción.")
        obj.save()
        form.save_m2m()
        return redirect(f"catalogos-{slug}-list")

@require_POST
def _catalog_delete(request, *, model, slug):
    _ensure_catalog_access(request)
    obj = get_object_or_404(model, pk=request.resolver_match.kwargs["pk"])
    if not can_manage_catalog_record(request.user, obj):
        messages.error(request, "No tienes permiso para realizar esta acción.")
        raise PermissionDenied("No tienes permiso para realizar esta acción.")
    result = _safe_delete_or_deactivate(obj)
    if result == "deleted":
        messages.success(request, "Registro eliminado correctamente.")
    elif result == "deactivated":
        messages.warning(request, "Registro desactivado porque está en uso.")
    else:
        messages.error(request, "El registro está en uso y este catálogo no tiene campo activo para desactivarlo.")
    return redirect(f"catalogos-{slug}-list")


def marcas_list(request): return _catalog_list(request, model=Marca, title="Marcas", slug="marcas", q_fields=["nombre"])
def marcas_create(request): return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca")
def marcas_edit(request, pk): return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca", pk=pk)
def marcas_delete(request, pk): return _catalog_delete(request, model=Marca, slug="marcas")

def modelos_list(request): return _catalog_list(request, model=ModeloVehiculo, title="Modelos", slug="modelos", q_fields=["nombre", "marca__nombre"])
def modelos_create(request): return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo")
def modelos_edit(request, pk): return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo", pk=pk)
def modelos_delete(request, pk): return _catalog_delete(request, model=ModeloVehiculo, slug="modelos")

def categorias_list(request): return _catalog_list(request, model=CategoriaPieza, title="Categorías", slug="categorias", q_fields=["nombre"])
def categorias_create(request): return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría")
def categorias_edit(request, pk): return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría", pk=pk)
def categorias_delete(request, pk): return _catalog_delete(request, model=CategoriaPieza, slug="categorias")

def nombres_piezas_list(request): return _catalog_list(request, model=NombrePieza, title="Nombres de piezas", slug="nombres-piezas", q_fields=["nombre_normalizado", "categoria__nombre"])
def nombres_piezas_create(request): return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza")
def nombres_piezas_edit(request, pk): return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza", pk=pk)
def nombres_piezas_delete(request, pk): return _catalog_delete(request, model=NombrePieza, slug="nombres-piezas")

def alias_piezas_list(request): return _catalog_list(request, model=AliasPieza, title="Alias de piezas", slug="alias-piezas", q_fields=["alias", "nombre_pieza__nombre_normalizado"])
def alias_piezas_create(request): return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza")
def alias_piezas_edit(request, pk): return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza", pk=pk)
def alias_piezas_delete(request, pk): return _catalog_delete(request, model=AliasPieza, slug="alias-piezas")
