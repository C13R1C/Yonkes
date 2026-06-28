from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.permissions import can_access_admin_area, can_manage_yonke, yonkes_queryset_for_user

from .models import Yonke
from .serializers import YonkeSerializer


class YonkePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return can_access_admin_area(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return yonkes_queryset_for_user(Yonke.objects.filter(pk=obj.pk), request.user).exists()
        return can_manage_yonke(request.user, obj)


class YonkeViewSet(viewsets.ModelViewSet):
    queryset = Yonke.objects.all().order_by("nombre")
    serializer_class = YonkeSerializer
    permission_classes = [YonkePermission]
    search_fields = ["nombre", "razon_social", "telefono", "email"]
    filterset_fields = ["estatus", "mostrar_contacto"]

    def get_queryset(self):
        return yonkes_queryset_for_user(super().get_queryset(), self.request.user)
