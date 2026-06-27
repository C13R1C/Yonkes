from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0003_catalogos_yonke"),
        ("yonkes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="marca",
            name="nombre",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="categoriapieza",
            name="nombre",
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name="marca",
            name="yonke",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="marcas_catalogo",
                to="yonkes.yonke",
            ),
        ),
        migrations.AddField(
            model_name="modelovehiculo",
            name="yonke",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modelos_catalogo",
                to="yonkes.yonke",
            ),
        ),
        migrations.AddField(
            model_name="categoriapieza",
            name="yonke",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categorias_catalogo",
                to="yonkes.yonke",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="marca",
            unique_together={("yonke", "nombre")},
        ),
        migrations.AlterUniqueTogether(
            name="modelovehiculo",
            unique_together={("yonke", "marca", "nombre")},
        ),
        migrations.AlterUniqueTogether(
            name="categoriapieza",
            unique_together={("yonke", "nombre")},
        ),
    ]
