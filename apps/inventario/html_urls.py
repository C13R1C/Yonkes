from django.urls import path

from . import html_views

app_name = "inventario_html"

urlpatterns = [
    path("vehiculos/", html_views.vehiculo_list, name="vehiculos-list"),
    path("vehiculos/nuevo/", html_views.vehiculo_create, name="vehiculos-create"),
    path("vehiculos/<int:pk>/", html_views.vehiculo_detail, name="vehiculos-detail"),
    path("vehiculos/<int:pk>/editar/", html_views.vehiculo_edit, name="vehiculos-edit"),
    path("piezas/", html_views.pieza_list, name="piezas-list"),
    path("piezas/nueva/", html_views.pieza_create, name="piezas-create"),
    path("piezas/<int:pk>/", html_views.pieza_detail, name="piezas-detail"),
    path("piezas/<int:pk>/editar/", html_views.pieza_edit, name="piezas-edit"),
]
