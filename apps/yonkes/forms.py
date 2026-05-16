from django import forms

from .models import Yonke


class YonkeForm(forms.ModelForm):
    class Meta:
        model = Yonke
        fields = [
            "nombre",
            "razon_social",
            "telefono",
            "whatsapp",
            "email",
            "direccion",
            "contacto_principal",
            "estatus",
            "mostrar_contacto",
            "notas_internas",
        ]
        widgets = {
            "direccion": forms.Textarea(attrs={"rows": 3, "class": "form-textarea"}),
            "notas_internas": forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in {"direccion", "notas_internas"}:
                field.widget.attrs.setdefault("class", "form-textarea")
            elif field.widget.__class__.__name__ == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif field.widget.__class__.__name__ == "CheckboxInput":
                field.widget.attrs.setdefault("class", "form-checkbox")
            else:
                field.widget.attrs.setdefault("class", "form-control")
