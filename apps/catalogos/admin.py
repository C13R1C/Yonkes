from django.contrib import admin
from .models import Marca, ModeloVehiculo, CategoriaPieza, NombrePieza, AliasPieza


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(ModeloVehiculo)
class ModeloVehiculoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "activo")
    search_fields = ("nombre", "marca__nombre")
    list_filter = ("marca", "activo")


@admin.register(CategoriaPieza)
class CategoriaPiezaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(NombrePieza)
class NombrePiezaAdmin(admin.ModelAdmin):
    list_display = ("nombre_normalizado", "categoria", "activo")
    search_fields = ("nombre_normalizado",)
    list_filter = ("categoria", "activo")


@admin.register(AliasPieza)
class AliasPiezaAdmin(admin.ModelAdmin):
    list_display = ("alias", "nombre_pieza")
    search_fields = ("alias", "nombre_pieza__nombre_normalizado")
