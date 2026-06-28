from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0002_imagen_principal"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vehiculo",
            options={"ordering": ["-actualizado_en"], "verbose_name": "Vehículo", "verbose_name_plural": "Vehículos"},
        ),
        migrations.AlterModelOptions(
            name="vehiculoimagen",
            options={"ordering": ["orden", "creado_en"], "verbose_name": "Imagen de vehículo", "verbose_name_plural": "Imágenes de vehículos"},
        ),
        migrations.AlterModelOptions(
            name="piezaimagen",
            options={"ordering": ["orden", "creado_en"], "verbose_name": "Imagen de pieza", "verbose_name_plural": "Imágenes de piezas"},
        ),
    ]
