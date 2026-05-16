from django.urls import path

from . import html_views

urlpatterns = [
    path("importaciones/", html_views.importaciones_list, name="importaciones-list"),
    path("importaciones/nueva/", html_views.importaciones_create, name="importaciones-create"),
    path("importaciones/<int:pk>/", html_views.importaciones_detail, name="importaciones-detail"),
]
