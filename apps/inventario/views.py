from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Vehiculo, Pieza
from .serializers import VehiculoSerializer, PiezaSerializer
from .filters import VehiculoFilter, PiezaFilter


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = (
        Vehiculo.objects
        .select_related("yonke", "marca", "modelo")
        .prefetch_related("imagenes")
        .all()
        .order_by("-actualizado_en")
    )
    serializer_class = VehiculoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VehiculoFilter
    search_fields = [
        "marca_texto",
        "modelo_texto",
        "version",
        "motor",
        "transmision",
        "ubicacion_fisica",
        "observaciones",
        "yonke__nombre",
    ]
    ordering_fields = ["anio", "ultima_actualizacion", "actualizado_en", "creado_en"]


class PiezaViewSet(viewsets.ModelViewSet):
    queryset = (
        Pieza.objects
        .select_related(
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PiezaFilter
    search_fields = [
        "nombre",
        "alias_local",
        "marca_texto",
        "modelo_texto",
        "ubicacion",
        "observaciones",
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
