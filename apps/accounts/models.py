from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ROLE_ADMIN_GENERAL = "admin_general"
    ROLE_DUENO_YONKE = "dueno_yonke"
    ROLE_EMPLEADO = "empleado"
    ROLE_BUSQUEDA = "usuario_busqueda"

    ROLE_CHOICES = [
        (ROLE_ADMIN_GENERAL, "Administrador general / CANACO"),
        (ROLE_DUENO_YONKE, "Dueno de yonke"),
        (ROLE_EMPLEADO, "Empleado con privilegios"),
        (ROLE_BUSQUEDA, "Usuario de busqueda"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    yonke = models.ForeignKey("yonkes.Yonke", on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    rol = models.CharField(max_length=50, choices=ROLE_CHOICES, default=ROLE_BUSQUEDA)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.user.username} - {self.rol}"
