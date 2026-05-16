from django import forms

from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            "yonke",
            "marca",
            "modelo",
            "anio",
            "version",
            "motor",
            "transmision",
            "vin",
            "numero_serie",
            "ubicacion_fisica",
            "observaciones",
            "datos_legales_internos",
            "estatus",
            "visibilidad",
        ]
        widgets = {
            "observaciones": forms.Textarea(attrs={"rows": 3, "class": "form-textarea"}),
            "datos_legales_internos": forms.Textarea(attrs={"rows": 3, "class": "form-textarea"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in {"observaciones", "datos_legales_internos"}:
                field.widget.attrs.setdefault("class", "form-textarea")
            elif field.widget.__class__.__name__ == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")
