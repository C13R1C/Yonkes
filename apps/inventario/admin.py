from django.contrib import admin
from .models import Vehiculo, Pieza, VehiculoImagen, PiezaImagen


class VehiculoImagenInline(admin.TabularInline):
    model = VehiculoImagen
    extra = 1


class PiezaImagenInline(admin.TabularInline):
    model = PiezaImagen
    extra = 1


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "yonke", "marca_texto", "modelo_texto", "anio", "estatus", "visibilidad", "ultima_actualizacion")
    list_filter = ("estatus", "visibilidad", "yonke", "anio")
    search_fields = ("marca_texto", "modelo_texto", "vin", "numero_serie", "ubicacion_fisica")
    inlines = [VehiculoImagenInline]


@admin.register(Pieza)
class PiezaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "yonke", "cantidad", "condicion", "estatus", "visibilidad", "precio", "precio_visible")
    list_filter = ("estatus", "visibilidad", "condicion", "precio_visible", "yonke")
    search_fields = ("nombre", "alias_local", "marca_texto", "modelo_texto", "ubicacion")
    inlines = [PiezaImagenInline]


@admin.register(VehiculoImagen)
class VehiculoImagenAdmin(admin.ModelAdmin):
    list_display = ("id", "vehiculo", "tipo", "orden", "creado_en")


@admin.register(PiezaImagen)
class PiezaImagenAdmin(admin.ModelAdmin):
    list_display = ("id", "pieza", "orden", "creado_en")
