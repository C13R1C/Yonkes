from django.urls import path

from . import html_views

urlpatterns = [
    path("vehiculos/", html_views.vehiculo_list, name="vehiculos-list"),
    path("vehiculos/nuevo/", html_views.vehiculo_create, name="vehiculos-create"),
    path("vehiculos/<int:pk>/", html_views.vehiculo_detail, name="vehiculos-detail"),
    path("vehiculos/<int:pk>/editar/", html_views.vehiculo_edit, name="vehiculos-edit"),
]
