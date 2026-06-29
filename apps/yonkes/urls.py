from rest_framework.routers import DefaultRouter

from .views import YonkeViewSet

app_name = "yonkes_api"

router = DefaultRouter()
router.register(r"yonkes", YonkeViewSet, basename="api-yonkes")

urlpatterns = router.urls

