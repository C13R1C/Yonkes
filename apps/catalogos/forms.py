from django import forms
from django.db.models import Q

from apps.accounts.permissions import is_admin_general, user_yonke
from apps.yonkes.models import Yonke

from .models import AliasPieza, CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from .policies import DUPLICATE_ERROR, can_edit_catalog_item, normalize_catalog_value, relation_queryset_for_user


def _scope_yonke(user):
    return None if is_admin_general(user) else user_yonke(user)


def _normalized_duplicate_exists(model, field_name, value, *, yonke, instance=None, extra_q=Q()):
    normalized = normalize_catalog_value(value)
    qs = model.objects.filter(extra_q)
    qs = qs.filter(yonke__isnull=True) if yonke is None else qs.filter(yonke=yonke)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    for obj in qs.only(field_name):
        if normalize_catalog_value(getattr(obj, field_name)) == normalized:
            return True
    return False


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self._configure_yonke_field()
        if "visibilidad" in self.fields:
            self.fields["visibilidad"].initial = self.fields["visibilidad"].initial or "privado"
            self.fields["visibilidad"].required = False
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

    def _configure_yonke_field(self):
        if "yonke" not in self.fields:
            return
        current_yonke = user_yonke(self.user)
        if is_admin_general(self.user):
            self.fields["yonke"].queryset = Yonke.objects.none()
            self.fields["yonke"].required = False
            self.fields["yonke"].disabled = True
            self.fields["yonke"].help_text = "CANACO crea catálogos globales."
            self.fields["yonke"].initial = None
        else:
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True

    def clean_yonke(self):
        return _scope_yonke(self.user)

    def clean_visibilidad(self):
        return self.cleaned_data.get("visibilidad") or "privado"

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.pk and not can_edit_catalog_item(self.user, self.instance):
            raise forms.ValidationError("No tienes permiso para editar este registro.")
        return cleaned


class MarcaForm(BaseStyledModelForm):
    class Meta:
        model = Marca
        fields = ["yonke", "nombre", "logo", "activo", "visibilidad"]
        labels = {"yonke": "Yonke", "nombre": "Nombre", "logo": "Logo", "activo": "Activo", "visibilidad": "Visibilidad"}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if nombre and _normalized_duplicate_exists(Marca, "nombre", nombre, yonke=_scope_yonke(self.user), instance=self.instance):
            raise forms.ValidationError(DUPLICATE_ERROR)
        return nombre


class ModeloVehiculoForm(BaseStyledModelForm):
    class Meta:
        model = ModeloVehiculo
        fields = ["yonke", "marca", "nombre", "activo", "visibilidad"]
        labels = {"yonke": "Yonke", "marca": "Marca", "nombre": "Nombre", "activo": "Activo", "visibilidad": "Visibilidad"}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["marca"].queryset = relation_queryset_for_user(Marca.objects.filter(activo=True).order_by("nombre"), user)

    def clean_marca(self):
        marca = self.cleaned_data.get("marca")
        if marca and not relation_queryset_for_user(Marca.objects.filter(pk=marca.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar marcas fuera de tu alcance permitido.")
        return marca

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        marca = self.cleaned_data.get("marca")
        if nombre and marca and _normalized_duplicate_exists(
            ModeloVehiculo,
            "nombre",
            nombre,
            yonke=_scope_yonke(self.user),
            instance=self.instance,
            extra_q=Q(marca=marca),
        ):
            raise forms.ValidationError(DUPLICATE_ERROR)
        return nombre


class CategoriaPiezaForm(BaseStyledModelForm):
    class Meta:
        model = CategoriaPieza
        fields = ["yonke", "nombre", "activo", "visibilidad"]
        labels = {"yonke": "Yonke", "nombre": "Nombre", "activo": "Activo", "visibilidad": "Visibilidad"}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if nombre and _normalized_duplicate_exists(CategoriaPieza, "nombre", nombre, yonke=_scope_yonke(self.user), instance=self.instance):
            raise forms.ValidationError(DUPLICATE_ERROR)
        return nombre


class NombrePiezaForm(BaseStyledModelForm):
    class Meta:
        model = NombrePieza
        fields = ["yonke", "nombre_normalizado", "categoria", "activo", "visibilidad"]
        labels = {
            "yonke": "Yonke",
            "nombre_normalizado": "Nombre normalizado",
            "categoria": "Categoría",
            "activo": "Activo",
            "visibilidad": "Visibilidad",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["categoria"].queryset = relation_queryset_for_user(CategoriaPieza.objects.filter(activo=True).order_by("nombre"), user)

    def clean_categoria(self):
        categoria = self.cleaned_data.get("categoria")
        if categoria and not relation_queryset_for_user(CategoriaPieza.objects.filter(pk=categoria.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar categorías fuera de tu alcance permitido.")
        return categoria

    def clean_nombre_normalizado(self):
        nombre = self.cleaned_data.get("nombre_normalizado")
        if nombre and _normalized_duplicate_exists(NombrePieza, "nombre_normalizado", nombre, yonke=_scope_yonke(self.user), instance=self.instance):
            raise forms.ValidationError(DUPLICATE_ERROR)
        return nombre


class AliasPiezaForm(BaseStyledModelForm):
    class Meta:
        model = AliasPieza
        fields = ["yonke", "nombre_pieza", "alias", "visibilidad"]
        labels = {"yonke": "Yonke", "nombre_pieza": "Nombre de pieza", "alias": "Alias", "visibilidad": "Visibilidad"}

    def _configure_yonke_field(self):
        super()._configure_yonke_field()
        if is_admin_general(self.user) and "yonke" in self.fields:
            self.fields["yonke"].help_text = "Los alias no son globales; CANACO solo los consulta."

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        if is_admin_general(user):
            self.fields["nombre_pieza"].queryset = NombrePieza.objects.none()
        else:
            self.fields["nombre_pieza"].queryset = relation_queryset_for_user(NombrePieza.objects.filter(activo=True).order_by("nombre_normalizado"), user)

    def clean_yonke(self):
        if is_admin_general(self.user):
            raise forms.ValidationError("Los alias de pieza deben pertenecer a un yonke.")
        return user_yonke(self.user)

    def clean_nombre_pieza(self):
        nombre_pieza = self.cleaned_data.get("nombre_pieza")
        if nombre_pieza and not relation_queryset_for_user(NombrePieza.objects.filter(pk=nombre_pieza.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar nombres de pieza fuera de tu alcance permitido.")
        return nombre_pieza

    def clean_alias(self):
        alias = self.cleaned_data.get("alias")
        nombre_pieza = self.cleaned_data.get("nombre_pieza")
        if alias and nombre_pieza and _normalized_duplicate_exists(
            AliasPieza,
            "alias",
            alias,
            yonke=user_yonke(self.user),
            instance=self.instance,
            extra_q=Q(nombre_pieza=nombre_pieza),
        ):
            raise forms.ValidationError(DUPLICATE_ERROR)
        return alias
