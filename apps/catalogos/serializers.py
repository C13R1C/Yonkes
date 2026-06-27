from rest_framework import serializers
from .models import Marca, ModeloVehiculo, CategoriaPieza, NombrePieza, AliasPieza


class MarcaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)

    class Meta:
        model = Marca
        fields = ["id", "yonke", "yonke_nombre", "nombre", "logo", "activo"]


class ModeloVehiculoSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)

    class Meta:
        model = ModeloVehiculo
        fields = ["id", "yonke", "yonke_nombre", "marca", "marca_nombre", "nombre", "activo"]


class CategoriaPiezaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)

    class Meta:
        model = CategoriaPieza
        fields = ["id", "yonke", "yonke_nombre", "nombre", "activo"]


class NombrePiezaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = NombrePieza
        fields = ["id", "yonke", "yonke_nombre", "nombre_normalizado", "categoria", "categoria_nombre", "activo"]


class AliasPiezaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    nombre_pieza_texto = serializers.CharField(source="nombre_pieza.nombre_normalizado", read_only=True)

    class Meta:
        model = AliasPieza
        fields = ["id", "yonke", "yonke_nombre", "nombre_pieza", "nombre_pieza_texto", "alias"]
