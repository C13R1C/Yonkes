from rest_framework import serializers
from .models import Vehiculo, Pieza, VehiculoImagen, PiezaImagen


class VehiculoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculoImagen
        fields = ["id", "imagen", "tipo", "orden", "creado_en"]


class PiezaImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiezaImagen
        fields = ["id", "imagen", "orden", "creado_en"]


class VehiculoSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    modelo_nombre = serializers.CharField(source="modelo.nombre", read_only=True)
    imagenes = VehiculoImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "yonke",
            "yonke_nombre",
            "marca",
            "marca_nombre",
            "modelo",
            "modelo_nombre",
            "marca_texto",
            "modelo_texto",
            "anio",
            "version",
            "motor",
            "transmision",
            "ubicacion_fisica",
            "observaciones",
            "estatus",
            "visibilidad",
            "fecha_ingreso",
            "ultima_actualizacion",
            "imagenes",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]


class PiezaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    vehiculo_texto = serializers.CharField(source="vehiculo.__str__", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    marca_compatible_nombre = serializers.CharField(source="marca_compatible.nombre", read_only=True)
    modelo_compatible_nombre = serializers.CharField(source="modelo_compatible.nombre", read_only=True)
    nombre_normalizado_texto = serializers.CharField(source="nombre_normalizado.nombre_normalizado", read_only=True)
    imagenes = PiezaImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Pieza
        fields = [
            "id",
            "yonke",
            "yonke_nombre",
            "vehiculo",
            "vehiculo_texto",
            "nombre",
            "nombre_normalizado",
            "nombre_normalizado_texto",
            "alias_local",
            "categoria",
            "categoria_nombre",
            "marca_compatible",
            "marca_compatible_nombre",
            "modelo_compatible",
            "modelo_compatible_nombre",
            "marca_texto",
            "modelo_texto",
            "anio_inicio",
            "anio_fin",
            "condicion",
            "estatus",
            "visibilidad",
            "precio",
            "precio_visible",
            "cantidad",
            "ubicacion",
            "observaciones",
            "ultima_actualizacion",
            "imagenes",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]


class PiezaBusquedaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    yonke_telefono = serializers.SerializerMethodField()
    yonke_whatsapp = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    precio_mostrado = serializers.SerializerMethodField()

    class Meta:
        model = Pieza
        fields = [
            "id",
            "nombre",
            "yonke_nombre",
            "yonke_telefono",
            "yonke_whatsapp",
            "categoria_nombre",
            "marca_texto",
            "modelo_texto",
            "anio_inicio",
            "anio_fin",
            "condicion",
            "estatus",
            "visibilidad",
            "cantidad",
            "precio_mostrado",
            "precio_visible",
            "ultima_actualizacion",
        ]

    def get_yonke_telefono(self, obj):
        if obj.yonke and obj.yonke.mostrar_contacto:
            return obj.yonke.telefono
        return None

    def get_yonke_whatsapp(self, obj):
        if obj.yonke and obj.yonke.mostrar_contacto:
            return obj.yonke.whatsapp
        return None

    def get_precio_mostrado(self, obj):
        if obj.precio_visible:
            return obj.precio
        return None
