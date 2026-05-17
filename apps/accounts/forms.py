from django import forms
from django.contrib.auth import get_user_model

from apps.yonkes.models import Yonke

from .models import UserProfile

User = get_user_model()


class UsuarioBaseForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    rol = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    yonke = forms.ModelChoiceField(queryset=Yonke.objects.all().order_by("nombre"), required=False)
    telefono = forms.CharField(max_length=30, required=False)
    activo = forms.BooleanField(required=False, initial=True)

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


class UsuarioCreateForm(UsuarioBaseForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)


class UsuarioEditForm(UsuarioBaseForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, min_length=8)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=8)
    telefono = forms.CharField(max_length=30, required=False)
    rol = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=False)
    yonke = forms.ModelChoiceField(queryset=Yonke.objects.all().order_by("nombre"), required=False)

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
            self.add_error("username", "Este username ya existe.")
        return cleaned


class ProfileSettingsForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    telefono = forms.CharField(max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
