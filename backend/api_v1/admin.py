from django.contrib import admin

from .models import CustomUser, Ingredient, IngredientInRecipe, FavoriteRecipe, \
    Follow, Recipe, ShoppingCart, Tag, TagsInRecipe


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'is_favorited', )

    def is_favorited(self, obj):
        return obj.is_favorited.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(TagsInRecipe)
class TagsInRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
