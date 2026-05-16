from django.db import models


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ModeloVehiculo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="modelos")
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Modelo de vehiculo"
        verbose_name_plural = "Modelos de vehiculo"
        unique_together = ["marca", "nombre"]
        ordering = ["marca__nombre", "nombre"]

    def __str__(self):
        return f"{self.marca} {self.nombre}"


class CategoriaPieza(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria de pieza"
        verbose_name_plural = "Categorias de piezas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class NombrePieza(models.Model):
    nombre_normalizado = models.CharField(max_length=150)
    categoria = models.ForeignKey(CategoriaPieza, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Nombre de pieza"
        verbose_name_plural = "Nombres de piezas"
        ordering = ["nombre_normalizado"]

    def __str__(self):
        return self.nombre_normalizado


class AliasPieza(models.Model):
    nombre_pieza = models.ForeignKey(NombrePieza, on_delete=models.CASCADE, related_name="alias")
    alias = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Alias de pieza"
        verbose_name_plural = "Alias de piezas"
        unique_together = ["nombre_pieza", "alias"]

    def __str__(self):
        return f"{self.alias} -> {self.nombre_pieza}"
