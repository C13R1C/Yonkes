from django import forms

from apps.accounts.permissions import is_admin_general, user_yonke

from .models import ImportacionExcel


class ImportacionExcelForm(forms.ModelForm):
    class Meta:
        model = ImportacionExcel
        fields = ["yonke", "tipo_importacion", "archivo"]

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        if not is_admin_general(user):
            self.fields["yonke"].queryset = self.fields["yonke"].queryset.filter(pk=getattr(current_yonke, "pk", None))
            if current_yonke:
                self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
        for field in self.fields.values():
            widget_name = field.widget.__class__.__name__
            if widget_name == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif widget_name == "ClearableFileInput":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_yonke(self):
        current_yonke = user_yonke(self.user)
        if is_admin_general(self.user):
            return self.cleaned_data["yonke"]
        return current_yonke
