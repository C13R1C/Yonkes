from django.db.models import Case, IntegerField, Q, Value, When
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import is_admin_general, user_yonke
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
        current_yonke = user_yonke(request.user)

        queryset = (
            Pieza.objects.select_related("yonke", "vehiculo", "vehiculo__marca", "categoria", "marca_compatible", "modelo_compatible")
            .exclude(estatus__in=["vendida", "agotada", "bloqueada", "no_visible"])
        )
        if is_admin_general(request.user):
            pass
        elif current_yonke:
            queryset = queryset.filter(Q(yonke=current_yonke) | Q(visibilidad="visible"))
        else:
            queryset = queryset.filter(visibilidad="visible")

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
                | Q(vehiculo__marca_texto__icontains=marca)
                | Q(vehiculo__marca__nombre__icontains=marca)
            )

        if modelo:
            queryset = queryset.filter(
                Q(modelo_texto__icontains=modelo)
                | Q(modelo_compatible__nombre__icontains=modelo)
                | Q(vehiculo__modelo_texto__icontains=modelo)
                | Q(vehiculo__modelo__nombre__icontains=modelo)
            )

        if anio.isdigit():
            anio_int = int(anio)
            queryset = queryset.filter(
                Q(anio_inicio__lte=anio_int, anio_fin__gte=anio_int)
                | Q(anio_inicio=anio_int)
                | Q(anio_fin=anio_int)
                | Q(vehiculo__anio=anio_int)
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

        if current_yonke and not is_admin_general(request.user):
            queryset = queryset.annotate(
                prioridad_yonke=Case(
                    When(yonke=current_yonke, then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            )
        else:
            queryset = queryset.annotate(prioridad_yonke=Value(0, output_field=IntegerField()))

        queryset = queryset.annotate(
            exactitud=Case(
                When(nombre__iexact=pieza, then=0),
                When(nombre__icontains=pieza, then=1),
                default=2,
                output_field=IntegerField(),
            )
        ).order_by("prioridad_yonke", "exactitud", "-ultima_actualizacion")

        serializer = PiezaBusquedaSerializer(queryset, many=True, context={"request": request})

        return Response({
            "total": queryset.count(),
            "resultados": serializer.data,
        })
