from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    yonke = models.ForeignKey("yonkes.Yonke", on_delete=models.SET_NULL, null=True, blank=True)

    accion = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    entidad_id = models.CharField(max_length=100, blank=True)

    cambios = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de auditoria"
        verbose_name_plural = "Logs de auditoria"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.accion} - {self.entidad} - {self.creado_en}"
