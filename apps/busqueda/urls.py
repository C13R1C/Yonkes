from django.urls import path
from .views import BusquedaPiezasAPIView

urlpatterns = [
    path("piezas/", BusquedaPiezasAPIView.as_view(), name="busqueda-piezas"),
]
