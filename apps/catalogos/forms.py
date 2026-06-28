from django import forms

from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget_name = field.widget.__class__.__name__
            if widget_name == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif widget_name == "CheckboxInput":
                field.widget.attrs.setdefault("class", "form-checkbox")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class MarcaForm(BaseStyledModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "activo"]


class ModeloVehiculoForm(BaseStyledModelForm):
    class Meta:
        model = ModeloVehiculo
        fields = ["marca", "nombre", "activo"]


class CategoriaPiezaForm(BaseStyledModelForm):
    class Meta:
        model = CategoriaPieza
        fields = ["nombre", "activo"]


class NombrePiezaForm(BaseStyledModelForm):
    class Meta:
        model = NombrePieza
        fields = ["nombre_normalizado", "categoria", "activo"]


class AliasPiezaForm(BaseStyledModelForm):
    class Meta:
        model = AliasPieza
        fields = ["nombre_pieza", "alias", "activo"]
