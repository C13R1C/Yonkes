import django_filters
from .models import Vehiculo, Pieza


class VehiculoFilter(django_filters.FilterSet):
    anio_min = django_filters.NumberFilter(field_name="anio", lookup_expr="gte")
    anio_max = django_filters.NumberFilter(field_name="anio", lookup_expr="lte")

    class Meta:
        model = Vehiculo
        fields = [
            "yonke",
            "marca",
            "modelo",
            "anio",
            "estatus",
            "visibilidad",
        ]


class PiezaFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = django_filters.NumberFilter(field_name="precio", lookup_expr="lte")
    anio = django_filters.NumberFilter(method="filter_anio")

    class Meta:
        model = Pieza
        fields = [
            "yonke",
            "categoria",
            "condicion",
            "estatus",
            "visibilidad",
            "precio_visible",
        ]

    def filter_anio(self, queryset, name, value):
        return queryset.filter(anio_inicio__lte=value, anio_fin__gte=value)
