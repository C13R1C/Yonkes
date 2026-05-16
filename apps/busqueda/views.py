from django.db.models import Q, Case, When, IntegerField
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.inventario.models import Pieza
from apps.inventario.serializers import PiezaBusquedaSerializer


class BusquedaPiezasAPIView(APIView):
    def get(self, request):
        pieza = request.query_params.get("pieza", "").strip()
        marca = request.query_params.get("marca", "").strip()
        modelo = request.query_params.get("modelo", "").strip()
        anio = request.query_params.get("anio", "").strip()
        categoria = request.query_params.get("categoria", "").strip()
        yonke = request.query_params.get("yonke", "").strip()
        condicion = request.query_params.get("condicion", "").strip()
        estatus = request.query_params.get("estatus", "").strip()
        solo_disponibles = request.query_params.get("solo_disponibles", "").lower() in ["1", "true", "si", "sí"]

        queryset = (
            Pieza.objects
            .select_related("yonke", "categoria", "marca_compatible", "modelo_compatible")
            .filter(visibilidad="visible")
            .exclude(estatus__in=["vendida", "agotada", "bloqueada", "no_visible"])
        )

        if pieza:
            queryset = queryset.filter(
                Q(nombre__icontains=pieza)
                | Q(alias_local__icontains=pieza)
                | Q(nombre_normalizado__nombre_normalizado__icontains=pieza)
            )

        if marca:
            queryset = queryset.filter(
                Q(marca_texto__icontains=marca)
                | Q(marca_compatible__nombre__icontains=marca)
            )

        if modelo:
            queryset = queryset.filter(
                Q(modelo_texto__icontains=modelo)
                | Q(modelo_compatible__nombre__icontains=modelo)
            )

        if anio.isdigit():
            anio_int = int(anio)
            queryset = queryset.filter(
                Q(anio_inicio__lte=anio_int, anio_fin__gte=anio_int)
                | Q(anio_inicio=anio_int)
                | Q(anio_fin=anio_int)
            )

        if categoria:
            queryset = queryset.filter(categoria__nombre__icontains=categoria)

        if yonke:
            queryset = queryset.filter(yonke__nombre__icontains=yonke)

        if condicion:
            queryset = queryset.filter(condicion=condicion)

        if estatus:
            queryset = queryset.filter(estatus=estatus)

        if solo_disponibles:
            queryset = queryset.filter(estatus="disponible", cantidad__gt=0)

        queryset = queryset.annotate(
            exactitud=Case(
                When(nombre__iexact=pieza, then=0),
                When(nombre__icontains=pieza, then=1),
                default=2,
                output_field=IntegerField(),
            )
        ).order_by("exactitud", "-ultima_actualizacion")

        serializer = PiezaBusquedaSerializer(queryset, many=True)

        return Response({
            "total": queryset.count(),
            "resultados": serializer.data,
        })
