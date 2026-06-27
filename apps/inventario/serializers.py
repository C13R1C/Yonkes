from rest_framework import serializers

from apps.accounts.permissions import can_view_sensitive_inventory, is_admin_general, user_yonke

from .models import Pieza, PiezaImagen, Vehiculo, VehiculoImagen


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
    marca_logo = serializers.SerializerMethodField()
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
            "marca_logo",
            "modelo",
            "modelo_nombre",
            "marca_texto",
            "modelo_texto",
            "imagen_principal",
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not can_view_sensitive_inventory(user, instance):
            data["ubicacion_fisica"] = None
            data["observaciones"] = ""
        return data

    def validate(self, attrs):
        marca = attrs.get("marca", getattr(self.instance, "marca", None))
        modelo = attrs.get("modelo", getattr(self.instance, "modelo", None))
        request = self.context.get("request")
        user = getattr(request, "user", None)
        current_yonke = user_yonke(user)
        current_yonke_id = getattr(current_yonke, "pk", None)

        if marca and not is_admin_general(user) and marca.yonke_id not in (None, current_yonke_id):
            raise serializers.ValidationError({"marca": "No puedes usar marcas de otro yonke."})
        if modelo and not is_admin_general(user) and modelo.yonke_id not in (None, current_yonke_id):
            raise serializers.ValidationError({"modelo": "No puedes usar modelos de otro yonke."})
        if modelo and modelo.marca and not is_admin_general(user) and modelo.marca.yonke_id not in (None, current_yonke_id):
            raise serializers.ValidationError({"modelo": "No puedes usar modelos de otro yonke."})
        if marca and modelo and modelo.marca_id != marca.pk:
            raise serializers.ValidationError({"modelo": "El modelo seleccionado no pertenece a la marca indicada."})
        return attrs

    def get_marca_logo(self, obj):
        if obj.marca and obj.marca.logo:
            return self._absolute_url(obj.marca.logo.url)
        return None

    def _absolute_url(self, path):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)
        return path


class PiezaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    vehiculo_texto = serializers.CharField(source="vehiculo.__str__", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    marca_compatible_nombre = serializers.CharField(source="marca_compatible.nombre", read_only=True)
    marca_compatible_logo = serializers.SerializerMethodField()
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
            "marca_compatible_logo",
            "modelo_compatible",
            "modelo_compatible_nombre",
            "marca_texto",
            "modelo_texto",
            "imagen_principal",
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not can_view_sensitive_inventory(user, instance):
            data["ubicacion"] = ""
            data["observaciones"] = ""
            if not instance.precio_visible:
                data["precio"] = None
        return data

    def get_marca_compatible_logo(self, obj):
        if obj.marca_compatible and obj.marca_compatible.logo:
            return self._absolute_url(obj.marca_compatible.logo.url)
        return None

    def _absolute_url(self, path):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)
        return path


class PiezaBusquedaSerializer(serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    yonke_telefono = serializers.SerializerMethodField()
    yonke_whatsapp = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    precio_mostrado = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    marca_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Pieza
        fields = [
            "id",
            "nombre",
            "yonke_nombre",
            "yonke_telefono",
            "yonke_whatsapp",
            "categoria_nombre",
            "imagen_url",
            "marca_logo_url",
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

    def _absolute_url(self, path):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)
        return path

    def get_imagen_url(self, obj):
        image = obj.imagen_principal or (obj.vehiculo.imagen_principal if obj.vehiculo else None)
        if image:
            return self._absolute_url(image.url)
        return None

    def get_marca_logo_url(self, obj):
        marca = obj.marca_compatible or (obj.vehiculo.marca if obj.vehiculo else None)
        if marca and marca.logo:
            return self._absolute_url(marca.logo.url)
        return None
