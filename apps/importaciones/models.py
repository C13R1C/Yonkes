from django.conf import settings
from django.db import models


class ImportacionExcel(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("validando", "Validando"),
        ("con_errores", "Con errores"),
        ("lista_para_importar", "Lista para importar"),
        ("importada", "Importada"),
        ("cancelada", "Cancelada"),
    ]

    TIPO_CHOICES = [
        ("vehiculos", "Vehiculos"),
        ("piezas", "Piezas"),
        ("piezas_sueltas", "Piezas sueltas"),
        ("mixto", "Mixto"),
    ]

    yonke = models.ForeignKey("yonkes.Yonke", on_delete=models.CASCADE, related_name="importaciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    tipo_importacion = models.CharField(max_length=50, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to="importaciones/")
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default="pendiente")

    total_filas = models.PositiveIntegerField(default=0)
    filas_validas = models.PositiveIntegerField(default=0)
    filas_con_error = models.PositiveIntegerField(default=0)

    resultado = models.JSONField(default=dict, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Importacion Excel"
        verbose_name_plural = "Importaciones Excel"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Importacion {self.id} - {self.yonke}"


class ImportacionError(models.Model):
    importacion = models.ForeignKey(ImportacionExcel, on_delete=models.CASCADE, related_name="errores")
    numero_fila = models.PositiveIntegerField()
    campo = models.CharField(max_length=100, blank=True)
    valor = models.TextField(blank=True)
    error = models.TextField()

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Error de importacion"
        verbose_name_plural = "Errores de importacion"
        ordering = ["numero_fila"]

    def __str__(self):
        return f"Fila {self.numero_fila}: {self.error}"
