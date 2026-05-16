from rest_framework.routers import DefaultRouter
from .views import (
    MarcaViewSet,
    ModeloVehiculoViewSet,
    CategoriaPiezaViewSet,
    NombrePiezaViewSet,
    AliasPiezaViewSet,
)

router = DefaultRouter()
router.register(r"marcas", MarcaViewSet, basename="marcas")
router.register(r"modelos", ModeloVehiculoViewSet, basename="modelos")
router.register(r"categorias", CategoriaPiezaViewSet, basename="categorias")
router.register(r"nombres-piezas", NombrePiezaViewSet, basename="nombres-piezas")
router.register(r"alias-piezas", AliasPiezaViewSet, basename="alias-piezas")

urlpatterns = router.urls
