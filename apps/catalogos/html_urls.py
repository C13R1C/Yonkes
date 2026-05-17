from django.urls import path

from . import html_views

urlpatterns = [
    path("catalogos/", html_views.index, name="catalogos-index"),
    path("catalogos/marcas/", html_views.marcas_list, name="catalogos-marcas-list"),
    path("catalogos/marcas/nuevo/", html_views.marcas_create, name="catalogos-marcas-create"),
    path("catalogos/marcas/<int:pk>/editar/", html_views.marcas_edit, name="catalogos-marcas-edit"),
    path("catalogos/modelos/", html_views.modelos_list, name="catalogos-modelos-list"),
    path("catalogos/modelos/nuevo/", html_views.modelos_create, name="catalogos-modelos-create"),
    path("catalogos/modelos/<int:pk>/editar/", html_views.modelos_edit, name="catalogos-modelos-edit"),
    path("catalogos/categorias/", html_views.categorias_list, name="catalogos-categorias-list"),
    path("catalogos/categorias/nuevo/", html_views.categorias_create, name="catalogos-categorias-create"),
    path("catalogos/categorias/<int:pk>/editar/", html_views.categorias_edit, name="catalogos-categorias-edit"),
    path("catalogos/nombres-piezas/", html_views.nombres_piezas_list, name="catalogos-nombres-piezas-list"),
    path("catalogos/nombres-piezas/nuevo/", html_views.nombres_piezas_create, name="catalogos-nombres-piezas-create"),
    path("catalogos/nombres-piezas/<int:pk>/editar/", html_views.nombres_piezas_edit, name="catalogos-nombres-piezas-edit"),
    path("catalogos/alias-piezas/", html_views.alias_piezas_list, name="catalogos-alias-piezas-list"),
    path("catalogos/alias-piezas/nuevo/", html_views.alias_piezas_create, name="catalogos-alias-piezas-create"),
    path("catalogos/alias-piezas/<int:pk>/editar/", html_views.alias_piezas_edit, name="catalogos-alias-piezas-edit"),
]
