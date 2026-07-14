from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ProfileSettingsForm, RegisterForm
from .models import UserProfile

User = get_user_model()


def _profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"rol": UserProfile.ROLE_BUSQUEDA, "activo": True})
    return profile


def _safe_next_url(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "/"
    if url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return "/"


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    next_url = _safe_next_url(request)
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Sesión iniciada correctamente.")
            return redirect(next_url)
        error = "Credenciales inválidas."
    return render(request, "accounts/login.html", {"next": next_url, "error": error})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            UserProfile.objects.create(
                user=user,
                rol=UserProfile.ROLE_BUSQUEDA,
                yonke=None,
                telefono=form.cleaned_data.get("telefono", ""),
                activo=True,
            )
        login(request, user)
        messages.success(request, "Cuenta creada correctamente.")
        return redirect("/")

    return render(request, "accounts/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("/login/")


@login_required(login_url="/login/")
def profile_view(request):
    profile = _profile(request.user)
    return render(request, "accounts/profile.html", {"active_module": "", "profile": profile})


@login_required(login_url="/login/")
def settings_view(request):
    profile = _profile(request.user)
    if request.method == "POST":
        form = ProfileSettingsForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            profile.telefono = form.cleaned_data["telefono"]
            profile.save()
            messages.success(request, "Configuración actualizada.")
            return redirect("/perfil/")
    else:
        form = ProfileSettingsForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "telefono": profile.telefono,
            }
        )
    return render(request, "accounts/settings.html", {"active_module": "", "form": form})
