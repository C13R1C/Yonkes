from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.yonkes.models import Yonke

from .forms import UsuarioCreateForm, UsuarioEditForm
from .models import UserProfile
from .permissions import is_admin_general, is_dueno_yonke, require_user_management, user_yonke

User = get_user_model()


def _get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"rol": UserProfile.ROLE_BUSQUEDA, "activo": True})
    return profile


@require_user_management
def usuarios_list(request):
    q = request.GET.get("q", "").strip()
    rol = request.GET.get("rol", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    activo = request.GET.get("activo", "").strip()

    users = User.objects.select_related("profile", "profile__yonke").order_by("-date_joined", "username")
    if is_dueno_yonke(request.user):
        users = users.filter(profile__yonke=user_yonke(request.user), profile__rol__in=[UserProfile.ROLE_EMPLEADO, UserProfile.ROLE_BUSQUEDA])
    if q:
        users = users.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(profile__telefono__icontains=q)
        )
    if rol:
        users = users.filter(profile__rol=rol)
    if yonke:
        users = users.filter(profile__yonke_id=yonke)
    if activo in {"true", "false"}:
        users = users.filter(profile__activo=(activo == "true"))

    for user in users:
        if not hasattr(user, "profile"):
            _get_or_create_profile(user)

    return render(
        request,
        "usuarios/list.html",
        {
            "active_module": "usuarios",
            "users": users,
            "roles": UserProfile.ROLE_CHOICES,
            "yonkes": Yonke.objects.all().order_by("nombre") if is_admin_general(request.user) else Yonke.objects.filter(pk=getattr(user_yonke(request.user), "pk", None)),
            "filters": {"q": q, "rol": rol, "yonke": yonke, "activo": activo},
        },
    )


@require_user_management
def usuarios_detail(request, pk):
    user = get_object_or_404(User.objects.select_related("profile", "profile__yonke"), pk=pk)
    profile = _get_or_create_profile(user)
    if is_dueno_yonke(request.user) and (profile.yonke_id != getattr(user_yonke(request.user), "pk", None) or profile.rol not in [UserProfile.ROLE_EMPLEADO, UserProfile.ROLE_BUSQUEDA]):
        raise PermissionDenied
    return render(request, "usuarios/detail.html", {"active_module": "usuarios", "user_obj": user, "profile": profile})


@require_user_management
def usuarios_create(request):
    form = UsuarioCreateForm(request.POST or None, actor=request.user)
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
                rol=form.cleaned_data["rol"],
                yonke=form.cleaned_data["yonke"],
                telefono=form.cleaned_data["telefono"],
                activo=form.cleaned_data["activo"],
            )
        messages.success(request, "Registro creado correctamente.")
        return redirect("usuarios-detail", pk=user.pk)
    return render(request, "usuarios/form.html", {"active_module": "usuarios", "form": form, "is_edit": False})


@require_user_management
def usuarios_edit(request, pk):
    user = get_object_or_404(User.objects.select_related("profile"), pk=pk)
    profile = _get_or_create_profile(user)
    if is_dueno_yonke(request.user) and (profile.yonke_id != getattr(user_yonke(request.user), "pk", None) or profile.rol not in [UserProfile.ROLE_EMPLEADO, UserProfile.ROLE_BUSQUEDA]):
        raise PermissionDenied

    if request.method == "POST":
        form = UsuarioEditForm(request.POST, actor=request.user)
        if form.is_valid():
            with transaction.atomic():
                user.username = form.cleaned_data["username"]
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.email = form.cleaned_data["email"]
                if form.cleaned_data.get("password"):
                    user.set_password(form.cleaned_data["password"])
                user.save()

                profile.rol = form.cleaned_data["rol"]
                profile.yonke = form.cleaned_data["yonke"]
                profile.telefono = form.cleaned_data["telefono"]
                profile.activo = form.cleaned_data["activo"]
                profile.save()
            messages.success(request, "Registro actualizado correctamente.")
            return redirect("usuarios-detail", pk=user.pk)
    else:
        form = UsuarioEditForm(
            initial={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "rol": profile.rol,
                "yonke": profile.yonke_id,
                "telefono": profile.telefono,
                "activo": profile.activo,
            },
            actor=request.user,
        )

    return render(request, "usuarios/form.html", {"active_module": "usuarios", "form": form, "is_edit": True, "user_obj": user})
