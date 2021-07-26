from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, IngredientViewSet,
                    TagViewSet, RecipeViewSet)

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
]
