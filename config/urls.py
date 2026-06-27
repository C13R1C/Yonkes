from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include(("apps.yonkes.html_urls", "yonkes_html"), namespace="yonkes_html")),
    path("", include(("apps.inventario.html_urls", "inventario_html"), namespace="inventario_html")),
    path("", include("apps.busqueda.html_urls")),
    path("", include("apps.catalogos.html_urls")),
    path("", include("apps.importaciones.html_urls")),
    path("", include("apps.auditoria.html_urls")),
    path("", include("apps.accounts.auth_urls")),
    path("", include("apps.accounts.html_urls")),
    path("", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),

    path("api/", include(("apps.yonkes.urls", "yonkes_api"), namespace="yonkes_api")),
    path("api/", include(("apps.inventario.urls", "inventario_api"), namespace="inventario_api")),
    path("api/catalogos/", include("apps.catalogos.urls")),
    path("api/busqueda/", include("apps.busqueda.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
