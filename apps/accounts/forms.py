from django import forms
from django.contrib.auth import get_user_model

from apps.yonkes.models import Yonke

from .models import UserProfile
from .permissions import is_admin_general, is_dueno_yonke, user_yonke

User = get_user_model()


class UsuarioBaseForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Correo electrónico", required=False)
    rol = forms.ChoiceField(label="Rol", choices=UserProfile.ROLE_CHOICES)
    yonke = forms.ModelChoiceField(label="Yonke", queryset=Yonke.objects.all().order_by("nombre"), required=False)
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)
    activo = forms.BooleanField(label="Activo", required=False, initial=True)

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        current_yonke = user_yonke(actor)
        if is_dueno_yonke(actor) and current_yonke:
            self.fields["rol"].choices = [
                choice for choice in UserProfile.ROLE_CHOICES if choice[0] in {UserProfile.ROLE_EMPLEADO, UserProfile.ROLE_BUSQUEDA}
            ]
            self.fields["yonke"].queryset = Yonke.objects.filter(pk=current_yonke.pk)
            self.fields["yonke"].initial = current_yonke
            self.fields["yonke"].disabled = True
        for field in self.fields.values():
            widget_name = field.widget.__class__.__name__
            if widget_name == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            elif widget_name == "CheckboxInput":
                field.widget.attrs.setdefault("class", "form-checkbox")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_rol(self):
        rol = self.cleaned_data["rol"]
        if is_dueno_yonke(self.actor) and rol not in {UserProfile.ROLE_EMPLEADO, UserProfile.ROLE_BUSQUEDA}:
            raise forms.ValidationError("Solo puedes crear o editar empleados y usuarios de búsqueda.")
        return rol

    def clean_yonke(self):
        current_yonke = user_yonke(self.actor)
        if is_admin_general(self.actor):
            return self.cleaned_data["yonke"]
        if is_dueno_yonke(self.actor):
            return current_yonke
        return self.cleaned_data["yonke"]


class UsuarioCreateForm(UsuarioBaseForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, min_length=8)


class UsuarioEditForm(UsuarioBaseForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=False, min_length=8)


class RegisterForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Correo electrónico", required=False)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput, min_length=8)
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)
    rol = forms.ChoiceField(label="Rol", choices=UserProfile.ROLE_CHOICES, required=False)
    yonke = forms.ModelChoiceField(label="Yonke", queryset=Yonke.objects.all().order_by("nombre"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget_name = field.widget.__class__.__name__
            if widget_name == "Select":
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            self.add_error("password_confirm", "Las contraseñas no coinciden.")
        if User.objects.filter(username=cleaned.get("username")).exists():
            self.add_error("username", "Este usuario ya existe.")
        return cleaned


class ProfileSettingsForm(forms.Form):
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)
    email = forms.EmailField(label="Correo electrónico", required=False)
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
