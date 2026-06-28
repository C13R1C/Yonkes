from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0002_marca_logo"),
        ("yonkes", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="categoriapieza",
            options={"ordering": ["nombre"], "verbose_name": "Categoría de pieza", "verbose_name_plural": "Categorías de piezas"},
        ),
        migrations.AlterModelOptions(
            name="modelovehiculo",
            options={"ordering": ["marca__nombre", "nombre"], "verbose_name": "Modelo de vehículo", "verbose_name_plural": "Modelos de vehículo"},
        ),
        migrations.AddField(
            model_name="nombrepieza",
            name="yonke",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="nombres_piezas_catalogo",
                to="yonkes.yonke",
            ),
        ),
        migrations.AddField(
            model_name="aliaspieza",
            name="yonke",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="alias_piezas_catalogo",
                to="yonkes.yonke",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="aliaspieza",
            unique_together={("yonke", "nombre_pieza", "alias")},
        ),
    ]
