from django import forms
from apps.accounts.permissions import is_admin_general, user_yonke
from apps.catalogos.models import CategoriaPieza, Marca, ModeloVehiculo, NombrePieza
from apps.catalogos.policies import relation_queryset_for_user

from .models import Pieza, Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            "yonke",
            "marca",
            "modelo",
            "imagen_principal",
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
        labels = {
            "yonke": "Yonke",
            "marca": "Marca",
            "modelo": "Modelo",
            "imagen_principal": "Imagen principal",
            "anio": "Año",
            "version": "Versión",
            "motor": "Motor",
            "transmision": "Transmisión",
            "vin": "VIN",
            "numero_serie": "Número de serie",
            "ubicacion_fisica": "Ubicación física",
            "observaciones": "Observaciones",
            "datos_legales_internos": "Datos legales internos",
            "estatus": "Estatus",
            "visibilidad": "Visibilidad",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        marca_id = self.data.get("marca") if self.data else getattr(self.instance, "marca_id", None)
        self.fields["modelo"].error_messages["invalid_choice"] = "El modelo seleccionado no pertenece a la marca indicada."

        marcas = relation_queryset_for_user(Marca.objects.filter(activo=True).order_by("nombre"), user)
        modelos = relation_queryset_for_user(ModeloVehiculo.objects.filter(activo=True).order_by("marca__nombre", "nombre"), user)
        self.fields["marca"].queryset = marcas
        if marca_id:
            self.fields["modelo"].queryset = modelos.filter(marca_id=marca_id)
        else:
            self.fields["modelo"].queryset = self.fields["modelo"].queryset.none()
        if not is_admin_general(user):
            self.fields["yonke"].queryset = self.fields["yonke"].queryset.filter(pk=getattr(current_yonke, "pk", None))
            if current_yonke:
                self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
        for name, field in self.fields.items():
            if name in {"observaciones", "datos_legales_internos"}:
                field.widget.attrs.setdefault("class", "form-textarea")
            elif field.widget.__class__.__name__ == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif field.widget.__class__.__name__ == "ClearableFileInput":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_yonke(self):
        current_yonke = user_yonke(self.user)
        if is_admin_general(self.user):
            return self.cleaned_data["yonke"]
        return current_yonke

    def clean_marca(self):
        marca = self.cleaned_data.get("marca")
        if marca and not relation_queryset_for_user(Marca.objects.filter(pk=marca.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar marcas fuera de tu alcance permitido.")
        return marca

    def clean_modelo(self):
        modelo = self.cleaned_data.get("modelo")
        if modelo and not relation_queryset_for_user(ModeloVehiculo.objects.filter(pk=modelo.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar modelos fuera de tu alcance permitido.")
        return modelo

    def clean(self):
        cleaned = super().clean()
        marca = cleaned.get("marca")
        modelo = cleaned.get("modelo")
        if marca and modelo and modelo.marca_id != marca.pk:
            self.add_error("modelo", "El modelo seleccionado no pertenece a la marca indicada.")
        return cleaned


class PiezaForm(forms.ModelForm):
    class Meta:
        model = Pieza
        fields = [
            "yonke",
            "vehiculo",
            "nombre",
            "nombre_normalizado",
            "alias_local",
            "categoria",
            "marca_compatible",
            "modelo_compatible",
            "imagen_principal",
            "anio_inicio",
            "anio_fin",
            "condicion",
            "estatus",
            "visibilidad",
            "precio",
            "precio_visible",
            "cantidad",
            "ubicacion",
            "observaciones",
        ]
        widgets = {
            "observaciones": forms.Textarea(attrs={"rows": 3, "class": "form-textarea"}),
        }
        labels = {
            "yonke": "Yonke",
            "vehiculo": "Vehículo",
            "nombre": "Nombre",
            "nombre_normalizado": "Nombre normalizado",
            "alias_local": "Alias local",
            "categoria": "Categoría",
            "marca_compatible": "Marca compatible",
            "modelo_compatible": "Modelo compatible",
            "imagen_principal": "Imagen principal",
            "anio_inicio": "Año inicial",
            "anio_fin": "Año final",
            "condicion": "Condición",
            "estatus": "Estatus",
            "visibilidad": "Visibilidad",
            "precio": "Precio",
            "precio_visible": "Precio visible",
            "cantidad": "Cantidad",
            "ubicacion": "Ubicación",
            "observaciones": "Observaciones",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(user)
        nombres = relation_queryset_for_user(NombrePieza.objects.filter(activo=True).order_by("nombre_normalizado"), user)
        self.fields["nombre_normalizado"].queryset = nombres
        self.fields["categoria"].queryset = relation_queryset_for_user(CategoriaPieza.objects.filter(activo=True).order_by("nombre"), user)
        self.fields["marca_compatible"].queryset = relation_queryset_for_user(Marca.objects.filter(activo=True).order_by("nombre"), user)
        self.fields["modelo_compatible"].queryset = relation_queryset_for_user(ModeloVehiculo.objects.filter(activo=True).order_by("marca__nombre", "nombre"), user)
        if not is_admin_general(user):
            self.fields["yonke"].queryset = self.fields["yonke"].queryset.filter(pk=getattr(current_yonke, "pk", None))
            self.fields["vehiculo"].queryset = self.fields["vehiculo"].queryset.filter(yonke=current_yonke)
            if current_yonke:
                self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
        for name, field in self.fields.items():
            if name == "observaciones":
                field.widget.attrs.setdefault("class", "form-textarea")
            elif field.widget.__class__.__name__ == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif field.widget.__class__.__name__ == "CheckboxInput":
                field.widget.attrs.setdefault("class", "form-checkbox")
            elif field.widget.__class__.__name__ == "ClearableFileInput":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_yonke(self):
        current_yonke = user_yonke(self.user)
        if is_admin_general(self.user):
            return self.cleaned_data["yonke"]
        return current_yonke

    def clean_vehiculo(self):
        vehiculo = self.cleaned_data.get("vehiculo")
        current_yonke = user_yonke(self.user)
        if vehiculo and not is_admin_general(self.user) and vehiculo.yonke_id != getattr(current_yonke, "pk", None):
            raise forms.ValidationError("No puedes asociar piezas a vehículos de otro yonke.")
        return vehiculo

    def clean_nombre_normalizado(self):
        nombre = self.cleaned_data.get("nombre_normalizado")
        if nombre and not relation_queryset_for_user(NombrePieza.objects.filter(pk=nombre.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar nombres de pieza fuera de tu alcance permitido.")
        return nombre

    def clean_categoria(self):
        categoria = self.cleaned_data.get("categoria")
        if categoria and not relation_queryset_for_user(CategoriaPieza.objects.filter(pk=categoria.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar categorías fuera de tu alcance permitido.")
        return categoria

    def clean_marca_compatible(self):
        marca = self.cleaned_data.get("marca_compatible")
        if marca and not relation_queryset_for_user(Marca.objects.filter(pk=marca.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar marcas fuera de tu alcance permitido.")
        return marca

    def clean_modelo_compatible(self):
        modelo = self.cleaned_data.get("modelo_compatible")
        if modelo and not relation_queryset_for_user(ModeloVehiculo.objects.filter(pk=modelo.pk), self.user).exists():
            raise forms.ValidationError("No puedes usar modelos fuera de tu alcance permitido.")
        return modelo
