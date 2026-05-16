from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include("apps.yonkes.html_urls")),
    path("", include("apps.inventario.html_urls")),
    path("", include("apps.busqueda.html_urls")),
    path("", include("apps.catalogos.html_urls")),
    path("", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),

    path("api/", include("apps.yonkes.urls")),
    path("api/", include("apps.inventario.urls")),
    path("api/catalogos/", include("apps.catalogos.urls")),
    path("api/busqueda/", include("apps.busqueda.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
