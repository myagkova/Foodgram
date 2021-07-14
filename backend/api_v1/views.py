from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import CustomUser, Ingredient, Recipe, Tag
from .serializers import (CustomUserSerializer, RecipeSerializer,
                          IngredientSerializer, TagSerializer)

from djoser import views


class CustomUserViewSet(views.UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
