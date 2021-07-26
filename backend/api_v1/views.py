from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import filters, viewsets, status
from .models import (CustomUser, Follow, Ingredient, IngredientInRecipe,
                     FavoriteRecipes, Recipe, ShoppingCart, Tag, TagsInRecipe)
from .serializers import ( CustomUserSerializer,
                          RecipeSerializer, FollowSerializer,
                          IngredientSerializer,
                          IngredientInRecipeSerializer,
                          TagSerializer, TagsInRecipeSerializer)
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['get', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        user = self.request.user
        following = get_object_or_404(CustomUser, id=id)
        follow = Follow.objects.filter(user=user, following=following)
        print(request.method)
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
        user = self.request.user
        follows = Follow.objects.filter(user=user)
        following = []
        for follow in follows:
            following.append(follow.following)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(following, request)
        serializer = FollowSerializer(result_page, context={'request': request},
                                    many=True)
        # serializer = FollowSerializer(instance=following,
        #                                 context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data)
        # return JsonResponse(serializer.data, safe=False)


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

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorites(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipes.objects.filter(user=user, recipe=recipe)
        if request.method == 'GET':
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
        elif request.method == 'DELETE':
            favorite.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'GET':
            if not shopping_cart.exists():
                is_in_shopping_cart = ShoppingCart.objects.create(user=user,
                                                              recipe=recipe)
                is_in_shopping_cart.save()
            serializer = RecipeSerializer(instance=recipe,
                                          context={'request': request})
            response_data = {}
            response_data['id'] = serializer.data['id']
            response_data['name'] = serializer.data['name']
            response_data['image'] = serializer.data['image']
            response_data['cooking_time'] = serializer.data['cooking_time']
            return JsonResponse(response_data)
        elif request.method == 'DELETE':
            shopping_cart.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, pk=None):
        user = self.request.user
        filename = "shopping_list.txt"
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipes = []
        for item in shopping_cart:
            recipes.append(item.recipe)
        ingredients = {}
        for recipe in recipes:
            ing_in_recipe = IngredientInRecipe.objects.filter(recipe=recipe)
            for ing in ing_in_recipe:
                if ing in ingredients:
                    ingredients[ing.ingredient.name] += ing.amount
                else:
                    ingredients[ing.ingredient.name] = (ing.amount, ing.ingredient.measurement_unit)
        print(ingredients)
        content = ''
        for k,v in ingredients.items():
            nl = '\n'
            content += f'{k} -- {v[0]} {v[1]}{nl}'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename)
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        print('INGREDIENT-FILTER')
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
