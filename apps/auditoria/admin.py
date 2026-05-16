from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "yonke", "accion", "entidad", "entidad_id", "creado_en")
    list_filter = ("accion", "entidad", "yonke")
    search_fields = ("accion", "entidad", "entidad_id", "usuario__username")
    readonly_fields = ("usuario", "yonke", "accion", "entidad", "entidad_id", "cambios", "ip_address", "user_agent", "creado_en")
