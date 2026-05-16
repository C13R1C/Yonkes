from rest_framework import viewsets
from .models import Yonke
from .serializers import YonkeSerializer


class YonkeViewSet(viewsets.ModelViewSet):
    queryset = Yonke.objects.all().order_by("nombre")
    serializer_class = YonkeSerializer
    search_fields = ["nombre", "razon_social", "telefono", "email"]
    filterset_fields = ["estatus", "mostrar_contacto"]
