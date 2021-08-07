from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from .filters import IngredientFilter, RecipeFilter
from .models import (CustomUser, FavoriteRecipe, Follow, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingCart, Tag)
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientInRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer)


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['get', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        user = self.request.user
        following = get_object_or_404(CustomUser, id=id)
        follow = Follow.objects.filter(user=user, following=following)
        if request.method == 'GET':
            if not follow.exists():
                new_follow = Follow.objects.create(user=user,
                                                   following=following)
                new_follow.save()
            serializer = FollowSerializer(instance=following,
                                               context={'request': request})
            return JsonResponse(serializer.data)
        elif request.method == 'DELETE':
            follow.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, request, *args, **kwargs):
        following = CustomUser.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(following, request)
        serializer = FollowSerializer(result_page, context={'request': request},
                                    many=True)
        return paginator.get_paginated_response(serializer.data)


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
    permission_classes = [IsAuthenticated]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    filterset_fields = ['is_favorited', 'is_in_shopping_cart', 'tags', ]

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

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if request.method == 'GET':
            if not favorite.exists():
                new_favorite = FavoriteRecipe.objects.create(user=user,
                                                              recipe=recipe)
                new_favorite.save()
            serializer = ShortRecipeSerializer(instance=recipe,
                                          context={'request': request})
            return JsonResponse(serializer.data)
        elif request.method == 'DELETE':
            favorite.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticatedOrReadOnly])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'GET':
            if not shopping_cart.exists():
                is_in_shopping_cart = ShoppingCart.objects.create(user=user,
                                                              recipe=recipe)
                is_in_shopping_cart.save()
            serializer = ShortRecipeSerializer(instance=recipe,
                                          context={'request': request})
            return JsonResponse(serializer.data)
        elif request.method == 'DELETE':
            shopping_cart.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticatedOrReadOnly])
    def download_shopping_cart(self, request, pk=None):
        filename = 'shopping_list.txt'
        recipes = Recipe.objects.filter(customer__user=request.user)
        ingredients = {}
        for recipe in recipes:
            ing_in_recipe = IngredientInRecipe.objects.filter(recipe=recipe)
            for ing in ing_in_recipe:
                if ing in ingredients:
                    ingredients[ing.ingredient.name] += ing.amount
                else:
                    ingredients[ing.ingredient.name] = (ing.amount,
                                            ing.ingredient.measurement_unit)
        content = ''
        for ingredient, amount in ingredients.items():
            nl = '\n'
            content += f'{ingredient} -- {amount[0]} {amount[1]}{nl}'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename)
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    filterset_fields = ['name', ]
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
