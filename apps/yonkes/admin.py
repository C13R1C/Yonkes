from django.contrib import admin
from .models import Yonke


@admin.register(Yonke)
class YonkeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estatus", "telefono", "email", "mostrar_contacto", "actualizado_en")
    list_filter = ("estatus", "mostrar_contacto")
    search_fields = ("nombre", "razon_social", "telefono", "email")
