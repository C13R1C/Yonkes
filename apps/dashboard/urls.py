from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="dashboard-index"),
    path("dashboard/", views.index, name="dashboard"),
    path("yonkes/", views.yonkes, name="yonkes-placeholder"),
    path("vehiculos/", views.vehiculos, name="vehiculos-placeholder"),
    path("piezas/", views.piezas, name="piezas-placeholder"),
    path("busqueda/", views.busqueda, name="busqueda-placeholder"),
    path("catalogos/", views.catalogos, name="catalogos-placeholder"),
    path("importaciones/", views.importaciones, name="importaciones-placeholder"),
    path("auditoria/", views.auditoria, name="auditoria-placeholder"),
    path("usuarios/", views.usuarios, name="usuarios-placeholder"),
]
