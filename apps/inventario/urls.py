from rest_framework.routers import DefaultRouter

from .views import PiezaViewSet, VehiculoViewSet

app_name = "inventario_api"

router = DefaultRouter()
router.register(r"vehiculos", VehiculoViewSet, basename="api-vehiculos")
router.register(r"piezas", PiezaViewSet, basename="api-piezas")

urlpatterns = router.urls
