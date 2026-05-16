from django.urls import path

from . import html_views

urlpatterns = [
    path("busqueda/", html_views.buscar_piezas, name="busqueda-html"),
]
