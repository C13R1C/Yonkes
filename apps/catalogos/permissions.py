from apps.accounts.models import UserProfile


EDIT_ROLES = {UserProfile.ROLE_ADMIN_GENERAL, UserProfile.ROLE_DUENO_YONKE, UserProfile.ROLE_EMPLEADO}
LOCAL_ROLES = {UserProfile.ROLE_DUENO_YONKE, UserProfile.ROLE_EMPLEADO}


def get_profile(user):
    if not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "profile", None)


def can_access_catalogs(user):
    profile = get_profile(user)
    return bool(profile and profile.activo and profile.rol in EDIT_ROLES)


def can_manage_catalog_record(user, obj=None):
    profile = get_profile(user)
    if not profile or not profile.activo or profile.rol not in EDIT_ROLES:
        return False
    owner_id = getattr(obj, "yonke_id", None) if obj is not None else None
    if profile.rol == UserProfile.ROLE_ADMIN_GENERAL:
        return owner_id is None
    if profile.rol in LOCAL_ROLES:
        return bool(profile.yonke_id and owner_id == profile.yonke_id)
    return False


def scope_catalog_queryset(user, queryset):
    profile = get_profile(user)
    if not profile or not profile.activo or profile.rol not in EDIT_ROLES:
        return queryset.none()
    if profile.rol == UserProfile.ROLE_ADMIN_GENERAL:
        return queryset.filter(yonke__isnull=True)
    if profile.rol in LOCAL_ROLES and profile.yonke_id:
        return queryset.filter(yonke_id=profile.yonke_id)
    return queryset.none()
