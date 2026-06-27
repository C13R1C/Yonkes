from django import forms

from apps.accounts.permissions import is_admin_general, user_yonke
from apps.yonkes.models import Yonke

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
            elif widget_name == "ClearableFileInput":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class MarcaForm(BaseStyledModelForm):
    class Meta:
        model = Marca
        fields = ["yonke", "nombre", "logo", "activo"]
        labels = {"yonke": "Yonke", "nombre": "Nombre", "logo": "Logo", "activo": "Activo"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        self.fields["yonke"].queryset = Yonke.objects.all().order_by("nombre")
        if not is_admin_general(user):
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True

    def clean_yonke(self):
        if is_admin_general(self.user):
            return self.cleaned_data.get("yonke")
        return user_yonke(self.user)


class ModeloVehiculoForm(BaseStyledModelForm):
    class Meta:
        model = ModeloVehiculo
        fields = ["yonke", "marca", "nombre", "activo"]
        labels = {"yonke": "Yonke", "marca": "Marca", "nombre": "Nombre", "activo": "Activo"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        self.fields["yonke"].queryset = Yonke.objects.all().order_by("nombre")
        marcas = Marca.objects.filter(activo=True).order_by("nombre")
        if not is_admin_general(user):
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
            marcas = marcas.filter(yonke=current_yonke)
        self.fields["marca"].queryset = marcas

    def clean_yonke(self):
        if is_admin_general(self.user):
            return self.cleaned_data.get("yonke")
        return user_yonke(self.user)

    def clean_marca(self):
        marca = self.cleaned_data.get("marca")
        current_yonke = user_yonke(self.user)
        if marca and not is_admin_general(self.user) and marca.yonke_id != getattr(current_yonke, "pk", None):
            raise forms.ValidationError("No puedes usar marcas de otro yonke.")
        return marca


class CategoriaPiezaForm(BaseStyledModelForm):
    class Meta:
        model = CategoriaPieza
        fields = ["yonke", "nombre", "activo"]
        labels = {"yonke": "Yonke", "nombre": "Nombre", "activo": "Activo"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        self.fields["yonke"].queryset = Yonke.objects.all().order_by("nombre")
        if not is_admin_general(user):
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True

    def clean_yonke(self):
        if is_admin_general(self.user):
            return self.cleaned_data.get("yonke")
        return user_yonke(self.user)


class NombrePiezaForm(BaseStyledModelForm):
    class Meta:
        model = NombrePieza
        fields = ["yonke", "nombre_normalizado", "categoria", "activo"]
        labels = {
            "yonke": "Yonke",
            "nombre_normalizado": "Nombre normalizado",
            "categoria": "Categoría",
            "activo": "Activo",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        self.fields["yonke"].queryset = Yonke.objects.all().order_by("nombre")
        categorias = CategoriaPieza.objects.filter(activo=True).order_by("nombre")
        if not is_admin_general(user):
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
            categorias = categorias.filter(yonke=current_yonke)
        self.fields["categoria"].queryset = categorias

    def clean_yonke(self):
        if is_admin_general(self.user):
            return self.cleaned_data.get("yonke")
        return user_yonke(self.user)

    def clean_categoria(self):
        categoria = self.cleaned_data.get("categoria")
        current_yonke = user_yonke(self.user)
        if categoria and not is_admin_general(self.user) and categoria.yonke_id != getattr(current_yonke, "pk", None):
            raise forms.ValidationError("No puedes usar categorías de otro yonke.")
        return categoria


class AliasPiezaForm(BaseStyledModelForm):
    class Meta:
        model = AliasPieza
        fields = ["yonke", "nombre_pieza", "alias"]
        labels = {"yonke": "Yonke", "nombre_pieza": "Nombre de pieza", "alias": "Alias"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        self.fields["yonke"].queryset = Yonke.objects.all().order_by("nombre")
        nombres = NombrePieza.objects.filter(activo=True).order_by("nombre_normalizado")
        if not is_admin_general(user):
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
            nombres = nombres.filter(yonke=current_yonke)
        self.fields["nombre_pieza"].queryset = nombres

    def clean_yonke(self):
        if is_admin_general(self.user):
            return self.cleaned_data.get("yonke")
        return user_yonke(self.user)

    def clean_nombre_pieza(self):
        nombre_pieza = self.cleaned_data.get("nombre_pieza")
        current_yonke = user_yonke(self.user)
        if nombre_pieza and not is_admin_general(self.user) and nombre_pieza.yonke_id != getattr(current_yonke, "pk", None):
            raise forms.ValidationError("No puedes usar nombres de pieza de otro yonke.")
        return nombre_pieza
