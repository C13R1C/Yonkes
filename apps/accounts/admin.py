from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "yonke", "activo", "actualizado_en")
    list_filter = ("rol", "activo", "yonke")
    search_fields = ("user__username", "user__email", "telefono")
