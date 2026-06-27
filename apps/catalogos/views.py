from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import is_admin_general, is_dueno_yonke, is_empleado, user_yonke, user_yonke_is_active

from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from .serializers import (
    AliasPiezaSerializer,
    CategoriaPiezaSerializer,
    MarcaSerializer,
    ModeloVehiculoSerializer,
    NombrePiezaSerializer,
)


def _is_catalog_operator(user):
    return is_dueno_yonke(user) or is_empleado(user)


def _can_access_catalogs(user):
    return bool(user and user.is_authenticated and (is_admin_general(user) or _is_catalog_operator(user)))


def _can_manage_catalogs(user):
    return bool(user and user.is_authenticated and _is_catalog_operator(user) and user_yonke_is_active(user))


def _same_yonke(user, obj):
    return getattr(obj, "yonke_id", None) == getattr(user_yonke(user), "pk", None)


class CatalogPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return False
        if request.method in permissions.SAFE_METHODS:
            return _can_access_catalogs(request.user)
        return _can_manage_catalogs(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return False
        if request.method in permissions.SAFE_METHODS:
            return _can_access_catalogs(request.user)
        return _same_yonke(request.user, obj)


class CatalogViewSetMixin:
    permission_classes = [CatalogPermission]
    related_yonke_fields = ()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if is_admin_general(user):
            selected_yonke = self.request.query_params.get("yonke")
            if selected_yonke:
                qs = qs.filter(yonke_id=selected_yonke)
            return qs

        if _is_catalog_operator(user) and user_yonke(user):
            return qs.filter(yonke=user_yonke(user))

        return qs.none()

    def _validate_related_yonke(self, serializer):
        current_yonke = user_yonke(self.request.user)
        current_yonke_id = getattr(current_yonke, "pk", None)

        for field_name in self.related_yonke_fields:
            related_obj = serializer.validated_data.get(field_name, getattr(serializer.instance, field_name, None))
            if related_obj and getattr(related_obj, "yonke_id", None) != current_yonke_id:
                raise PermissionDenied("No puedes usar registros de catalogo de otro yonke.")

    def perform_create(self, serializer):
        if not _can_manage_catalogs(self.request.user):
            raise PermissionDenied("No tienes permiso para administrar catalogos.")
        self._validate_related_yonke(serializer)
        serializer.save(yonke=user_yonke(self.request.user))

    def perform_update(self, serializer):
        if not _same_yonke(self.request.user, serializer.instance):
            raise PermissionDenied("No tienes permiso para administrar catalogos de otro yonke.")
        self._validate_related_yonke(serializer)
        serializer.save(yonke=serializer.instance.yonke)


class MarcaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = Marca.objects.select_related("yonke").all().order_by("nombre")
    serializer_class = MarcaSerializer
    search_fields = ["nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "activo"]


class ModeloVehiculoViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = ModeloVehiculo.objects.select_related("yonke", "marca").all().order_by("marca__nombre", "nombre")
    serializer_class = ModeloVehiculoSerializer
    search_fields = ["nombre", "marca__nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "marca", "activo"]
    related_yonke_fields = ("marca",)

    def get_queryset(self):
        user = self.request.user
        marca_id = self.request.query_params.get("marca")

        if not (_is_catalog_operator(user) and user_yonke(user) and marca_id):
            return super().get_queryset()

        return self.queryset.filter(marca_id=marca_id).filter(Q(yonke=user_yonke(user)) | Q(yonke__isnull=True))


class CategoriaPiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = CategoriaPieza.objects.select_related("yonke").all().order_by("nombre")
    serializer_class = CategoriaPiezaSerializer
    search_fields = ["nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "activo"]


class NombrePiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = NombrePieza.objects.select_related("yonke", "categoria").all().order_by("nombre_normalizado")
    serializer_class = NombrePiezaSerializer
    search_fields = ["nombre_normalizado", "categoria__nombre", "yonke__nombre"]
    filterset_fields = ["yonke", "categoria", "activo"]
    related_yonke_fields = ("categoria",)


class AliasPiezaViewSet(CatalogViewSetMixin, viewsets.ModelViewSet):
    queryset = AliasPieza.objects.select_related("yonke", "nombre_pieza").all().order_by("alias")
    serializer_class = AliasPiezaSerializer
    search_fields = ["alias", "nombre_pieza__nombre_normalizado", "yonke__nombre"]
    filterset_fields = ["yonke", "nombre_pieza"]
    related_yonke_fields = ("nombre_pieza",)
