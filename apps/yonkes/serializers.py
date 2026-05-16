from rest_framework import serializers
from .models import Yonke


class YonkeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Yonke
        fields = [
            "id",
            "nombre",
            "razon_social",
            "telefono",
            "whatsapp",
            "email",
            "direccion",
            "contacto_principal",
            "estatus",
            "mostrar_contacto",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]
