from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AliasPiezaForm, CategoriaPiezaForm, MarcaForm, ModeloVehiculoForm, NombrePiezaForm
from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza


def index(request):
    cards = [
        {"slug": "marcas", "title": "Marcas", "description": "Marcas base para vehículos y compatibilidad de piezas.", "total": Marca.objects.count()},
        {"slug": "modelos", "title": "Modelos", "description": "Modelos de vehículo vinculados a cada marca.", "total": ModeloVehiculo.objects.count()},
        {"slug": "categorias", "title": "Categorías", "description": "Clasificación principal de tipos de piezas.", "total": CategoriaPieza.objects.count()},
        {"slug": "nombres-piezas", "title": "Nombres de piezas", "description": "Nombres normalizados para búsquedas y catálogo.", "total": NombrePieza.objects.count()},
        {"slug": "alias-piezas", "title": "Alias de piezas", "description": "Sinónimos y variantes de nombres de piezas.", "total": AliasPieza.objects.count()},
    ]
    return render(request, "catalogos/index.html", {"active_module": "catalogos", "cards": cards})


def _catalog_list(request, *, model, title, slug, q_fields):
    q = request.GET.get("q", "").strip()
    qs = model.objects.all()
    if q:
        query = Q()
        for field in q_fields:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query)
    return render(request, "catalogos/list.html", {"active_module": "catalogos", "title": title, "slug": slug, "rows": qs, "q": q})


def _catalog_form(request, *, model, form_class, slug, title, pk=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"catalogos-{slug}-list")
    return render(request, "catalogos/form.html", {"active_module": "catalogos", "title": title, "slug": slug, "form": form, "is_edit": bool(pk)})


def marcas_list(request):
    return _catalog_list(request, model=Marca, title="Marcas", slug="marcas", q_fields=["nombre"])


def marcas_create(request):
    return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca")


def marcas_edit(request, pk):
    return _catalog_form(request, model=Marca, form_class=MarcaForm, slug="marcas", title="Marca", pk=pk)


def modelos_list(request):
    return _catalog_list(request, model=ModeloVehiculo, title="Modelos", slug="modelos", q_fields=["nombre", "marca__nombre"])


def modelos_create(request):
    return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo")


def modelos_edit(request, pk):
    return _catalog_form(request, model=ModeloVehiculo, form_class=ModeloVehiculoForm, slug="modelos", title="Modelo", pk=pk)


def categorias_list(request):
    return _catalog_list(request, model=CategoriaPieza, title="Categorías", slug="categorias", q_fields=["nombre"])


def categorias_create(request):
    return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría")


def categorias_edit(request, pk):
    return _catalog_form(request, model=CategoriaPieza, form_class=CategoriaPiezaForm, slug="categorias", title="Categoría", pk=pk)


def nombres_piezas_list(request):
    return _catalog_list(request, model=NombrePieza, title="Nombres de piezas", slug="nombres-piezas", q_fields=["nombre_normalizado", "categoria__nombre"])


def nombres_piezas_create(request):
    return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza")


def nombres_piezas_edit(request, pk):
    return _catalog_form(request, model=NombrePieza, form_class=NombrePiezaForm, slug="nombres-piezas", title="Nombre de pieza", pk=pk)


def alias_piezas_list(request):
    return _catalog_list(request, model=AliasPieza, title="Alias de piezas", slug="alias-piezas", q_fields=["alias", "nombre_pieza__nombre_normalizado"])


def alias_piezas_create(request):
    return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza")


def alias_piezas_edit(request, pk):
    return _catalog_form(request, model=AliasPieza, form_class=AliasPiezaForm, slug="alias-piezas", title="Alias de pieza", pk=pk)
