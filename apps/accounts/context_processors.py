from .permissions import can_access_admin_area, can_create_inventory, can_create_operational_catalog, can_manage_users, is_admin_general


def role_permissions(request):
    user = getattr(request, "user", None)
    return {
        "perm_is_admin_general": is_admin_general(user),
        "perm_can_access_admin_area": can_access_admin_area(user),
        "perm_can_access_catalogs": can_access_admin_area(user) or can_create_operational_catalog(user),
        "perm_can_create_inventory": can_create_inventory(user),
        "perm_can_manage_users": can_manage_users(user),
    }
