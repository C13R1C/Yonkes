from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect

from .models import UserProfile


VISIBLE_VALUE = "visible"


def user_profile(user):
    if not user or not user.is_authenticated:
        return None
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"rol": UserProfile.ROLE_BUSQUEDA, "activo": True},
    )
    return profile


def user_role(user):
    if user and user.is_superuser:
        return UserProfile.ROLE_ADMIN_GENERAL
    profile = user_profile(user)
    if not profile or not profile.activo:
        return None
    return profile.rol


def is_admin_general(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user_role(user) == UserProfile.ROLE_ADMIN_GENERAL))


def is_dueno_yonke(user):
    return user_role(user) == UserProfile.ROLE_DUENO_YONKE


def is_empleado(user):
    return user_role(user) == UserProfile.ROLE_EMPLEADO


def is_usuario_busqueda(user):
    return user_role(user) == UserProfile.ROLE_BUSQUEDA


def user_yonke(user):
    profile = user_profile(user)
    return profile.yonke if profile else None


def user_yonke_is_active(user):
    yonke = user_yonke(user)
    return bool(yonke and yonke.estatus == "activo")


def same_yonke(user, yonke):
    current_yonke = user_yonke(user)
    return bool(current_yonke and yonke and current_yonke.pk == yonke.pk)


def can_manage_yonke(user, yonke):
    return is_admin_general(user)


def can_edit_inventory(user, obj):
    if not user or not user.is_authenticated:
        return False
    if is_admin_general(user):
        return False
    return user_yonke_is_active(user) and (is_dueno_yonke(user) or is_empleado(user)) and same_yonke(user, getattr(obj, "yonke", None))


def can_view_inventory(user, obj):
    if is_admin_general(user) or same_yonke(user, getattr(obj, "yonke", None)):
        return True
    return getattr(obj, "visibilidad", None) == VISIBLE_VALUE


def can_view_sensitive_inventory(user, obj):
    return is_admin_general(user) or same_yonke(user, getattr(obj, "yonke", None))


def can_create_inventory(user):
    return user_yonke_is_active(user) and (is_dueno_yonke(user) or is_empleado(user))


def can_access_admin_area(user):
    return is_admin_general(user)


def can_create_operational_catalog(user):
    return user_yonke_is_active(user) and (is_dueno_yonke(user) or is_empleado(user))


def can_create_global_catalog(user):
    return is_admin_general(user)


def can_edit_catalog_item(user, obj):
    if is_admin_general(user):
        return not hasattr(obj, "yonke")
    return user_yonke_is_active(user) and (is_dueno_yonke(user) or is_empleado(user)) and same_yonke(user, getattr(obj, "yonke", None))


def catalog_queryset_for_user(queryset, user):
    model_fields = {field.name for field in queryset.model._meta.fields}
    if is_admin_general(user):
        return queryset
    yonke = user_yonke(user)
    if yonke and (is_dueno_yonke(user) or is_empleado(user)):
        if "yonke" in model_fields:
            return queryset.filter(Q(yonke__isnull=True) | Q(yonke=yonke))
        return queryset
    if "yonke" in model_fields:
        return queryset.filter(yonke__isnull=True)
    return queryset


def can_manage_users(user):
    return is_admin_general(user) or (user_yonke_is_active(user) and is_dueno_yonke(user))


def inventory_queryset_for_user(queryset, user):
    if is_admin_general(user):
        return queryset
    yonke = user_yonke(user)
    if yonke and (is_dueno_yonke(user) or is_empleado(user)):
        return queryset.filter(Q(yonke=yonke) | Q(visibilidad=VISIBLE_VALUE))
    return queryset.filter(visibilidad=VISIBLE_VALUE)


def own_yonke_queryset_for_user(queryset, user):
    if is_admin_general(user):
        return queryset
    yonke = user_yonke(user)
    if yonke and (is_dueno_yonke(user) or is_empleado(user)):
        return queryset.filter(yonke=yonke)
    return queryset.none()


def yonkes_queryset_for_user(queryset, user):
    if is_admin_general(user):
        return queryset
    yonke = user_yonke(user)
    if yonke and (is_dueno_yonke(user) or is_empleado(user)):
        return queryset.filter(pk=yonke.pk)
    return queryset.filter(estatus="activo", mostrar_contacto=True)


def require_admin_area(view_func):
    @wraps(view_func)
    @login_required(login_url="/login/")
    def wrapper(request, *args, **kwargs):
        if not can_access_admin_area(request.user):
            messages.error(request, "No tienes permiso para realizar esta acción.")
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def require_user_management(view_func):
    @wraps(view_func)
    @login_required(login_url="/login/")
    def wrapper(request, *args, **kwargs):
        if not can_manage_users(request.user):
            messages.error(request, "No tienes permiso para administrar usuarios.")
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def redirect_if_no_inventory_create_permission(view_func):
    @wraps(view_func)
    @login_required(login_url="/login/")
    def wrapper(request, *args, **kwargs):
        if not can_create_inventory(request.user):
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect("/busqueda/")
        return view_func(request, *args, **kwargs)

    return wrapper
