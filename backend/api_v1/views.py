from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import CustomUser, Ingredient, IngredientInRecipe, Recipe, Tag
from .serializers import (CustomUserSerializer, RecipeSerializer,
                          IngredientSerializer, IngredientInRecipeSerializer,
                          TagSerializer)

from djoser import views


class CustomUserViewSet(views.UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
    permission_classes = [IsAuthenticated]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(ingredients=self.request.data['ingredients'])


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
