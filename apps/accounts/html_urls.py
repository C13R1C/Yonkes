from django.urls import path

from . import html_views

urlpatterns = [
    path("usuarios/", html_views.usuarios_list, name="usuarios-list"),
    path("usuarios/nuevo/", html_views.usuarios_create, name="usuarios-create"),
    path("usuarios/<int:pk>/", html_views.usuarios_detail, name="usuarios-detail"),
    path("usuarios/<int:pk>/editar/", html_views.usuarios_edit, name="usuarios-edit"),
]
