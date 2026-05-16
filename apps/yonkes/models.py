from django.db import models


class Yonke(models.Model):
    ESTATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("activo", "Activo"),
        ("suspendido", "Suspendido"),
        ("inactivo", "Inactivo"),
        ("dado_de_baja", "Dado de baja"),
    ]

    nombre = models.CharField(max_length=150)
    razon_social = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    contacto_principal = models.CharField(max_length=150, blank=True)
    estatus = models.CharField(max_length=30, choices=ESTATUS_CHOICES, default="pendiente")
    mostrar_contacto = models.BooleanField(default=True)
    notas_internas = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Yonke"
        verbose_name_plural = "Yonkes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
