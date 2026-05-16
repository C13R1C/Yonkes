from rest_framework import serializers
from .models import Marca, ModeloVehiculo, CategoriaPieza, NombrePieza, AliasPieza


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "activo"]


class ModeloVehiculoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)

    class Meta:
        model = ModeloVehiculo
        fields = ["id", "marca", "marca_nombre", "nombre", "activo"]


class CategoriaPiezaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPieza
        fields = ["id", "nombre", "activo"]


class NombrePiezaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = NombrePieza
        fields = ["id", "nombre_normalizado", "categoria", "categoria_nombre", "activo"]


class AliasPiezaSerializer(serializers.ModelSerializer):
    nombre_pieza_texto = serializers.CharField(source="nombre_pieza.nombre_normalizado", read_only=True)

    class Meta:
        model = AliasPieza
        fields = ["id", "nombre_pieza", "nombre_pieza_texto", "alias"]
