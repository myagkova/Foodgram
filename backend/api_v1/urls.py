from django.urls import include, path, re_path


urlpatterns = [
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),

]
