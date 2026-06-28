from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import is_admin_general, user_yonke

from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from .policies import can_access_catalogs, can_edit_catalog_item, can_manage_catalogs, catalog_queryset_for_user, relation_queryset_for_user
from .serializers import (
    AliasPiezaSerializer,
    CategoriaPiezaSerializer,
    MarcaSerializer,
    ModeloVehiculoSerializer,
    NombrePiezaSerializer,
)


class CatalogPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return False
        if request.method in permissions.SAFE_METHODS:
            return can_access_catalogs(request.user)
        return can_manage_catalogs(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return False
        if request.method in permissions.SAFE_METHODS:
            return catalog_queryset_for_user(obj.__class__.objects.filter(pk=obj.pk), request.user).exists()
        return can_edit_catalog_item(request.user, obj)


class CatalogViewSetMixin:
    permission_classes = [CatalogPermission]
    related_yonke_fields = ()
    include_global_scope = True

    def get_queryset(self):
        qs = super().get_queryset()
        return catalog_queryset_for_user(qs, self.request.user, selected_yonke=self.request.query_params.get("yonke", ""), include_alias_shared=self.include_global_scope)

    def _validate_related_scope(self, serializer):
        for field_name in self.related_yonke_fields:
            related_obj = serializer.validated_data.get(field_name, getattr(serializer.instance, field_name, None))
            if related_obj and not relation_queryset_for_user(related_obj.__class__.objects.filter(pk=related_obj.pk), self.request.user).exists():
                raise PermissionDenied("No puedes usar registros de catálogo fuera de tu alcance permitido.")

    def perform_create(self, serializer):
        if not can_manage_catalogs(self.request.user):
            raise PermissionDenied("No tienes permiso para administrar catálogos.")
        if not self.include_global_scope and is_admin_general(self.request.user):
            raise PermissionDenied("Los alias de pieza deben pertenecer a un yonke.")
        self._validate_related_scope(serializer)
        serializer.save(yonke=None if is_admin_general(self.request.user) else user_yonke(self.request.user))

    def perform_update(self, serializer):
        if not can_edit_catalog_item(self.request.user, serializer.instance):
            raise PermissionDenied("No tienes permiso para editar este catálogo.")
        self._validate_related_scope(serializer)
        serializer.save(yonke=serializer.instance.yonke)


class MarcaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = Marca.objects.select_related("yonke").all().order_by("nombre")
    serializer_class = MarcaSerializer
    search_fields = ["nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "activo", "visibilidad"]


class ModeloVehiculoViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = ModeloVehiculo.objects.select_related("yonke", "marca").all().order_by("marca__nombre", "nombre")
    serializer_class = ModeloVehiculoSerializer
    search_fields = ["nombre", "marca__nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "marca", "activo", "visibilidad"]
    related_yonke_fields = ("marca",)

    def get_queryset(self):
        marca_id = self.request.query_params.get("marca")
        qs = super().get_queryset()
        if marca_id:
            qs = qs.filter(marca_id=marca_id)
        return qs


class CategoriaPiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = CategoriaPieza.objects.select_related("yonke").all().order_by("nombre")
    serializer_class = CategoriaPiezaSerializer
    search_fields = ["nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "activo", "visibilidad"]


class NombrePiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = NombrePieza.objects.select_related("yonke", "categoria").all().order_by("nombre_normalizado")
    serializer_class = NombrePiezaSerializer
    search_fields = ["nombre_normalizado", "categoria__nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "categoria", "activo", "visibilidad"]
    related_yonke_fields = ("categoria",)


class AliasPiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = AliasPieza.objects.select_related("yonke", "nombre_pieza").all().order_by("alias")
    serializer_class = AliasPiezaSerializer
    search_fields = ["alias", "nombre_pieza__nombre_normalizado", "yonke__nombre"]
    filterset_fields = ["yonke", "nombre_pieza", "visibilidad"]
    related_yonke_fields = ("nombre_pieza",)
    include_global_scope = False
