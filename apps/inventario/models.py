from django.conf import settings
from django.db import models
from django.utils import timezone


class Vehiculo(models.Model):
    ESTATUS_CHOICES = [
        ("disponible", "Disponible"),
        ("en_revision", "En revision"),
        ("en_desarme", "En desarme"),
        ("parcialmente_desarmado", "Parcialmente desarmado"),
        ("desarmado", "Desarmado"),
        ("vendido_completo", "Vendido completo"),
        ("dado_de_baja", "Dado de baja"),
        ("archivado", "Archivado"),
        ("bloqueado", "Bloqueado"),
        ("en_revision_legal", "En revision legal"),
    ]

    VISIBILIDAD_CHOICES = [
        ("visible", "Visible"),
        ("oculto", "Oculto"),
        ("privado", "Privado"),
        ("bloqueado", "Bloqueado"),
    ]

    yonke = models.ForeignKey("yonkes.Yonke", on_delete=models.CASCADE, related_name="vehiculos")
    marca = models.ForeignKey("catalogos.Marca", on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.ForeignKey("catalogos.ModeloVehiculo", on_delete=models.SET_NULL, null=True, blank=True)

    marca_texto = models.CharField(max_length=100, blank=True)
    modelo_texto = models.CharField(max_length=100, blank=True)
    anio = models.PositiveIntegerField(null=True, blank=True)
    version = models.CharField(max_length=100, blank=True)
    motor = models.CharField(max_length=100, blank=True)
    transmision = models.CharField(max_length=100, blank=True)

    vin = models.CharField(max_length=50, blank=True)
    numero_serie = models.CharField(max_length=50, blank=True)

    ubicacion_fisica = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)
    datos_legales_internos = models.TextField(blank=True)

    estatus = models.CharField(max_length=50, choices=ESTATUS_CHOICES, default="disponible")
    visibilidad = models.CharField(max_length=30, choices=VISIBILIDAD_CHOICES, default="visible")

    fecha_ingreso = models.DateField(null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(default=timezone.now)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehiculo"
        verbose_name_plural = "Vehiculos"
        ordering = ["-actualizado_en"]

    def __str__(self):
        marca = self.marca_texto or self.marca or ""
        modelo = self.modelo_texto or self.modelo or ""
        return f"{marca} {modelo} {self.anio or ''}".strip()


class Pieza(models.Model):
    ESTATUS_CHOICES = [
        ("disponible", "Disponible"),
        ("apartada", "Apartada"),
        ("vendida", "Vendida"),
        ("danada", "Danada"),
        ("pendiente_revision", "Pendiente de revision"),
        ("no_visible", "No visible"),
        ("agotada", "Agotada"),
        ("bloqueada", "Bloqueada"),
    ]

    CONDICION_CHOICES = [
        ("nueva", "Nueva"),
        ("usada", "Usada"),
        ("reparada", "Reparada"),
        ("danada", "Danada"),
        ("para_reparacion", "Para reparacion"),
        ("desconocida", "Desconocida"),
    ]

    VISIBILIDAD_CHOICES = [
        ("visible", "Visible"),
        ("oculto", "Oculto"),
        ("privado", "Privado"),
        ("bloqueado", "Bloqueado"),
    ]

    yonke = models.ForeignKey("yonkes.Yonke", on_delete=models.CASCADE, related_name="piezas")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name="piezas")

    nombre = models.CharField(max_length=150)
    nombre_normalizado = models.ForeignKey("catalogos.NombrePieza", on_delete=models.SET_NULL, null=True, blank=True)
    alias_local = models.CharField(max_length=150, blank=True)
    categoria = models.ForeignKey("catalogos.CategoriaPieza", on_delete=models.SET_NULL, null=True, blank=True)

    marca_compatible = models.ForeignKey("catalogos.Marca", on_delete=models.SET_NULL, null=True, blank=True)
    modelo_compatible = models.ForeignKey("catalogos.ModeloVehiculo", on_delete=models.SET_NULL, null=True, blank=True)

    marca_texto = models.CharField(max_length=100, blank=True)
    modelo_texto = models.CharField(max_length=100, blank=True)
    anio_inicio = models.PositiveIntegerField(null=True, blank=True)
    anio_fin = models.PositiveIntegerField(null=True, blank=True)

    condicion = models.CharField(max_length=50, choices=CONDICION_CHOICES, default="usada")
    estatus = models.CharField(max_length=50, choices=ESTATUS_CHOICES, default="disponible")
    visibilidad = models.CharField(max_length=30, choices=VISIBILIDAD_CHOICES, default="visible")

    precio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_visible = models.BooleanField(default=False)
    cantidad = models.PositiveIntegerField(default=1)

    ubicacion = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)

    ultima_actualizacion = models.DateTimeField(default=timezone.now)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pieza"
        verbose_name_plural = "Piezas"
        ordering = ["-actualizado_en"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["estatus"]),
            models.Index(fields=["visibilidad"]),
            models.Index(fields=["ultima_actualizacion"]),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.yonke}"


class VehiculoImagen(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="vehiculos/")
    tipo = models.CharField(max_length=50, blank=True)
    orden = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de vehiculo"
        verbose_name_plural = "Imagenes de vehiculos"
        ordering = ["orden", "creado_en"]

    def __str__(self):
        return f"Imagen vehiculo {self.vehiculo_id}"


class PiezaImagen(models.Model):
    pieza = models.ForeignKey(Pieza, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="piezas/")
    orden = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de pieza"
        verbose_name_plural = "Imagenes de piezas"
        ordering = ["orden", "creado_en"]

    def __str__(self):
        return f"Imagen pieza {self.pieza_id}"
