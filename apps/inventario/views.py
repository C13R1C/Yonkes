from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.accounts.permissions import inventory_queryset_for_user, is_admin_general, user_yonke

from .filters import PiezaFilter, VehiculoFilter
from .models import Pieza, Vehiculo
from .permissions import InventoryPermission
from .serializers import PiezaSerializer, VehiculoSerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = (
        Vehiculo.objects.select_related("yonke", "marca", "modelo")
        .prefetch_related("imagenes")
        .all()
        .order_by("-actualizado_en")
    )
    serializer_class = VehiculoSerializer
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VehiculoFilter
    search_fields = [
        "marca_texto",
        "modelo_texto",
        "version",
        "motor",
        "transmision",
        "yonke__nombre",
    ]
    ordering_fields = ["anio", "ultima_actualizacion", "actualizado_en", "creado_en"]

    def get_queryset(self):
        return inventory_queryset_for_user(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        yonke = serializer.validated_data.get("yonke") if is_admin_general(self.request.user) else user_yonke(self.request.user)
        serializer.save(creado_por=self.request.user, yonke=yonke)

    def perform_update(self, serializer):
        if is_admin_general(self.request.user):
            serializer.save()
        else:
            serializer.save(yonke=serializer.instance.yonke)


class PiezaViewSet(viewsets.ModelViewSet):
    queryset = (
        Pieza.objects.select_related(
            "yonke",
            "vehiculo",
            "categoria",
            "marca_compatible",
            "modelo_compatible",
            "nombre_normalizado",
        )
        .prefetch_related("imagenes")
        .all()
        .order_by("-actualizado_en")
    )
    serializer_class = PiezaSerializer
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PiezaFilter
    search_fields = [
        "nombre",
        "alias_local",
        "marca_texto",
        "modelo_texto",
        "yonke__nombre",
        "categoria__nombre",
    ]
    ordering_fields = [
        "precio",
        "cantidad",
        "ultima_actualizacion",
        "actualizado_en",
        "creado_en",
    ]

    def get_queryset(self):
        return inventory_queryset_for_user(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        yonke = serializer.validated_data.get("yonke") if is_admin_general(self.request.user) else user_yonke(self.request.user)
        vehiculo = serializer.validated_data.get("vehiculo")
        if vehiculo and not is_admin_general(self.request.user) and vehiculo.yonke_id != getattr(yonke, "pk", None):
            raise PermissionDenied("No puedes asociar piezas a vehículos de otro yonke.")
        serializer.save(creado_por=self.request.user, yonke=yonke)

    def perform_update(self, serializer):
        vehiculo = serializer.validated_data.get("vehiculo", serializer.instance.vehiculo)
        if vehiculo and not is_admin_general(self.request.user) and vehiculo.yonke_id != serializer.instance.yonke_id:
            raise PermissionDenied("No puedes asociar piezas a vehículos de otro yonke.")
        if is_admin_general(self.request.user):
            serializer.save()
        else:
            serializer.save(yonke=serializer.instance.yonke)
