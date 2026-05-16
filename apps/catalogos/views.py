from rest_framework import viewsets
from .models import Marca, ModeloVehiculo, CategoriaPieza, NombrePieza, AliasPieza
from .serializers import (
    MarcaSerializer,
    ModeloVehiculoSerializer,
    CategoriaPiezaSerializer,
    NombrePiezaSerializer,
    AliasPiezaSerializer,
)


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all().order_by("nombre")
    serializer_class = MarcaSerializer
    search_fields = ["nombre"]
    filterset_fields = ["activo"]


class ModeloVehiculoViewSet(viewsets.ModelViewSet):
    queryset = ModeloVehiculo.objects.select_related("marca").all().order_by("marca__nombre", "nombre")
    serializer_class = ModeloVehiculoSerializer
    search_fields = ["nombre", "marca__nombre"]
    filterset_fields = ["marca", "activo"]


class CategoriaPiezaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaPieza.objects.all().order_by("nombre")
    serializer_class = CategoriaPiezaSerializer
    search_fields = ["nombre"]
    filterset_fields = ["activo"]


class NombrePiezaViewSet(viewsets.ModelViewSet):
    queryset = NombrePieza.objects.select_related("categoria").all().order_by("nombre_normalizado")
    serializer_class = NombrePiezaSerializer
    search_fields = ["nombre_normalizado", "categoria__nombre"]
    filterset_fields = ["categoria", "activo"]


class AliasPiezaViewSet(viewsets.ModelViewSet):
    queryset = AliasPieza.objects.select_related("nombre_pieza").all().order_by("alias")
    serializer_class = AliasPiezaSerializer
    search_fields = ["alias", "nombre_pieza__nombre_normalizado"]
    filterset_fields = ["nombre_pieza"]
