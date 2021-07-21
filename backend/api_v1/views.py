from django.http import HttpResponse, JsonResponse
from requests import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import filters, viewsets, status
from .models import (CustomUser, Ingredient, IngredientInRecipe, FavoriteRecipes,
                     Recipe, Tag, TagsInRecipe)
from .serializers import (CustomUserSerializer, RecipeSerializer,
                          IngredientSerializer,
                          IngredientInRecipeSerializer,
                          TagSerializer, TagsInRecipeSerializer)
from rest_framework.generics import get_object_or_404

from djoser import views


class CustomUserViewSet(views.UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
    permission_classes = [IsAuthenticated]


class TagsInRecipe(viewsets.ModelViewSet):
    queryset = TagsInRecipe.objects.all()
    serializer_class = TagsInRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['author', 'tags', 'is_favorited']
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            ingredients=self.request.data['ingredients'],
            tags=self.request.data['tags']
        )

    def perform_update(self, serializer):
        serializer.save(
            ingredients=self.request.data['ingredients'],
            tags=self.request.data['tags']
        )

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated])
    def favorites(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipes.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            new_favorite = FavoriteRecipes.objects.create(user=user,
                                                          recipe=recipe)
            new_favorite.save()
        serializer = RecipeSerializer(instance=recipe)
        response_data = {}
        response_data['id'] = serializer.data['id']
        response_data['name'] = serializer.data['name']
        response_data['image'] = serializer.data['image']
        response_data['cooking_time'] = serializer.data['cooking_time']
        return JsonResponse(response_data)








class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
