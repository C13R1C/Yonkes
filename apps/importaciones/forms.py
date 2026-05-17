from django import forms

from .models import ImportacionExcel


class ImportacionExcelForm(forms.ModelForm):
    class Meta:
        model = ImportacionExcel
        fields = ["yonke", "tipo_importacion", "archivo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget_name = field.widget.__class__.__name__
            if widget_name == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif widget_name == "ClearableFileInput":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")
