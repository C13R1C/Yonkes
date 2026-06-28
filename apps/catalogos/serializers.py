from django.db.models import Q
from rest_framework import serializers

from apps.accounts.permissions import is_admin_general, user_yonke

from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from .policies import DUPLICATE_ERROR, normalize_catalog_value, relation_queryset_for_user


def _scope_yonke(user):
    return None if is_admin_general(user) else user_yonke(user)


def _duplicate(model, field, value, *, yonke, instance=None, extra_q=Q()):
    qs = model.objects.filter(extra_q)
    qs = qs.filter(yonke__isnull=True) if yonke is None else qs.filter(yonke=yonke)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    normalized = normalize_catalog_value(value)
    return any(normalize_catalog_value(getattr(obj, field)) == normalized for obj in qs.only(field))


class CatalogSerializerMixin:
    def _user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self._user()
        if "yonke" in attrs:
            attrs["yonke"] = None if is_admin_general(user) else user_yonke(user)
        return attrs


class MarcaSerializer(CatalogSerializerMixin, serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)

    class Meta:
        model = Marca
        fields = ["id", "yonke", "yonke_nombre", "nombre", "logo", "activo", "visibilidad"]

    def validate_nombre(self, value):
        if _duplicate(Marca, "nombre", value, yonke=_scope_yonke(self._user()), instance=self.instance):
            raise serializers.ValidationError(DUPLICATE_ERROR)
        return value


class ModeloVehiculoSerializer(CatalogSerializerMixin, serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)

    class Meta:
        model = ModeloVehiculo
        fields = ["id", "yonke", "yonke_nombre", "marca", "marca_nombre", "nombre", "activo", "visibilidad"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self._user()
        marca = attrs.get("marca", getattr(self.instance, "marca", None))
        nombre = attrs.get("nombre", getattr(self.instance, "nombre", ""))
        if marca and not relation_queryset_for_user(Marca.objects.filter(pk=marca.pk), user).exists():
            raise serializers.ValidationError({"marca": "No puedes usar marcas fuera de tu alcance permitido."})
        if marca and nombre and _duplicate(ModeloVehiculo, "nombre", nombre, yonke=_scope_yonke(user), instance=self.instance, extra_q=Q(marca=marca)):
            raise serializers.ValidationError({"nombre": DUPLICATE_ERROR})
        return attrs


class CategoriaPiezaSerializer(CatalogSerializerMixin, serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)

    class Meta:
        model = CategoriaPieza
        fields = ["id", "yonke", "yonke_nombre", "nombre", "activo", "visibilidad"]

    def validate_nombre(self, value):
        if _duplicate(CategoriaPieza, "nombre", value, yonke=_scope_yonke(self._user()), instance=self.instance):
            raise serializers.ValidationError(DUPLICATE_ERROR)
        return value


class NombrePiezaSerializer(CatalogSerializerMixin, serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = NombrePieza
        fields = ["id", "yonke", "yonke_nombre", "nombre_normalizado", "categoria", "categoria_nombre", "activo", "visibilidad"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self._user()
        categoria = attrs.get("categoria", getattr(self.instance, "categoria", None))
        nombre = attrs.get("nombre_normalizado", getattr(self.instance, "nombre_normalizado", ""))
        if categoria and not relation_queryset_for_user(CategoriaPieza.objects.filter(pk=categoria.pk), user).exists():
            raise serializers.ValidationError({"categoria": "No puedes usar categorías fuera de tu alcance permitido."})
        if nombre and _duplicate(NombrePieza, "nombre_normalizado", nombre, yonke=_scope_yonke(user), instance=self.instance):
            raise serializers.ValidationError({"nombre_normalizado": DUPLICATE_ERROR})
        return attrs


class AliasPiezaSerializer(CatalogSerializerMixin, serializers.ModelSerializer):
    yonke_nombre = serializers.CharField(source="yonke.nombre", read_only=True)
    nombre_pieza_texto = serializers.CharField(source="nombre_pieza.nombre_normalizado", read_only=True)

    class Meta:
        model = AliasPieza
        fields = ["id", "yonke", "yonke_nombre", "nombre_pieza", "nombre_pieza_texto", "alias", "visibilidad"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self._user()
        if is_admin_general(user):
            raise serializers.ValidationError("Los alias de pieza deben pertenecer a un yonke.")
        nombre_pieza = attrs.get("nombre_pieza", getattr(self.instance, "nombre_pieza", None))
        alias = attrs.get("alias", getattr(self.instance, "alias", ""))
        if nombre_pieza and not relation_queryset_for_user(NombrePieza.objects.filter(pk=nombre_pieza.pk), user).exists():
            raise serializers.ValidationError({"nombre_pieza": "No puedes usar nombres de pieza fuera de tu alcance permitido."})
        if nombre_pieza and alias and _duplicate(AliasPieza, "alias", alias, yonke=user_yonke(user), instance=self.instance, extra_q=Q(nombre_pieza=nombre_pieza)):
            raise serializers.ValidationError({"alias": DUPLICATE_ERROR})
        attrs["yonke"] = user_yonke(user)
        return attrs
