from django.contrib import admin
from django.urls import include, path, re_path


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^api/", include("djoser.urls.base")),
    path('api/', include('backend.api_v1.urls')),
]
