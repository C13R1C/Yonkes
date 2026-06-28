from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.permissions import can_create_inventory, can_edit_inventory, can_view_inventory


class InventoryPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return can_create_inventory(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return can_view_inventory(request.user, obj)
        return can_edit_inventory(request.user, obj)
