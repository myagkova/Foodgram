import django_filters

from .models import Ingredient, Recipe, TagsInRecipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method='is_favorited_filter')
    is_in_shopping_cart = django_filters.CharFilter(
        method='is_in_shopping_cart_filter')
    tags = django_filters.CharFilter(method='tags_filter')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'tags']

    def is_favorited_filter(self, queryset, name, value):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited and self.request.user.is_authenticated:
            return queryset.filter(is_favorited__user=self.request.user)
        return Recipe.objects.none()

    def is_in_shopping_cart_filter(self, queryset, name, value):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart and self.request.user.is_authenticated:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return Recipe.objects.none()

    def tags_filter(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        if (len(tags) != 0):
            recipes_with_tags = TagsInRecipe.objects.filter(
                tag__slug__in=tags).values_list('recipe', flat=True)
            return queryset.filter(id__in=recipes_with_tags)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='ingredients_filter')

    class Meta:
        model = Ingredient
        fields = ['name']

    def ingredients_filter(self, queryset, name, value):
        name = self.request.query_params.get('name')
        if name is not None:
            return queryset.filter(name__icontains=name)
        return queryset
