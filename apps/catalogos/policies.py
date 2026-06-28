from django.db.models import Q

from apps.accounts.permissions import is_admin_general, is_dueno_yonke, is_empleado, user_yonke, user_yonke_is_active

VISIBILIDAD_PRIVADO = "privado"
VISIBILIDAD_RED = "red"
DUPLICATE_ERROR = "Ya existe un registro equivalente."


def normalize_catalog_value(value):
    return " ".join((value or "").strip().casefold().split())


def is_catalog_operator(user):
    return is_dueno_yonke(user) or is_empleado(user)


def can_access_catalogs(user):
    return bool(user and user.is_authenticated and (is_admin_general(user) or is_catalog_operator(user)))


def can_manage_catalogs(user):
    if is_admin_general(user):
        return True
    return bool(user and user.is_authenticated and is_catalog_operator(user) and user_yonke_is_active(user))


def can_create_catalogs(user):
    return can_manage_catalogs(user)


def catalog_scope_q(user, *, include_alias_shared=True):
    if is_admin_general(user):
        return Q()
    current_yonke = user_yonke(user)
    if is_catalog_operator(user) and current_yonke:
        scope = Q(yonke__isnull=True) | Q(yonke=current_yonke) | Q(visibilidad=VISIBILIDAD_RED)
        if not include_alias_shared:
            scope = Q(yonke=current_yonke) | Q(visibilidad=VISIBILIDAD_RED)
        return scope
    return Q(pk__in=[])


def catalog_queryset_for_user(queryset, user, *, selected_yonke="", include_alias_shared=True):
    if is_admin_general(user):
        if selected_yonke == "global":
            return queryset.filter(yonke__isnull=True)
        if selected_yonke:
            return queryset.filter(yonke_id=selected_yonke)
        return queryset
    if is_catalog_operator(user):
        return queryset.filter(catalog_scope_q(user, include_alias_shared=include_alias_shared)).distinct()
    return queryset.none()


def relation_queryset_for_user(queryset, user, *, include_alias_shared=True):
    return catalog_queryset_for_user(queryset, user, include_alias_shared=include_alias_shared)


def can_edit_catalog_item(user, obj):
    if not user or not user.is_authenticated:
        return False
    if is_admin_general(user):
        return getattr(obj, "yonke_id", None) is None
    current_yonke = user_yonke(user)
    return bool(
        user_yonke_is_active(user)
        and is_catalog_operator(user)
        and current_yonke
        and getattr(obj, "yonke_id", None) == current_yonke.pk
    )


def owner_label(obj):
    return obj.yonke.nombre if getattr(obj, "yonke", None) else "Global"


def scope_label(obj, user=None):
    if getattr(obj, "yonke_id", None) is None:
        return "Global"
    current_yonke = user_yonke(user) if user is not None else None
    if current_yonke and obj.yonke_id == current_yonke.pk:
        return "Propio"
    if getattr(obj, "visibilidad", VISIBILIDAD_PRIVADO) == VISIBILIDAD_RED:
        return "Compartido"
    return "Privado"


def visibility_choices():
    return [(VISIBILIDAD_PRIVADO, "Privado"), (VISIBILIDAD_RED, "Red")]
