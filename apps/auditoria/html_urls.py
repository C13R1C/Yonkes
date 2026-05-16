from django.urls import path

from . import html_views

urlpatterns = [
    path("auditoria/", html_views.auditoria_list, name="auditoria-list"),
    path("auditoria/<int:pk>/", html_views.auditoria_detail, name="auditoria-detail"),
]
