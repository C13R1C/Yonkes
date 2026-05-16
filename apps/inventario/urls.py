from rest_framework.routers import DefaultRouter
from .views import VehiculoViewSet, PiezaViewSet

router = DefaultRouter()
router.register(r"vehiculos", VehiculoViewSet, basename="vehiculos")
router.register(r"piezas", PiezaViewSet, basename="piezas")

urlpatterns = router.urls
