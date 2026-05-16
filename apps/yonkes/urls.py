from rest_framework.routers import DefaultRouter
from .views import YonkeViewSet

router = DefaultRouter()
router.register(r"yonkes", YonkeViewSet, basename="yonkes")

urlpatterns = router.urls
