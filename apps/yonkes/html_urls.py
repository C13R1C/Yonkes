from django.urls import path

from . import html_views

app_name = "yonkes_html"

urlpatterns = [
    path("yonkes/", html_views.yonke_list, name="yonkes-list"),
    path("yonkes/nuevo/", html_views.yonke_create, name="yonkes-create"),
    path("yonkes/<int:pk>/", html_views.yonke_detail, name="yonkes-detail"),
    path("yonkes/<int:pk>/editar/", html_views.yonke_edit, name="yonkes-edit"),
]
