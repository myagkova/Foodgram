from rest_framework import serializers
from .models import CustomUser, Ingredient, IngredientInRecipe, Recipe, Tag
import logging

logging.basicConfig(level=logging.INFO)


class CustomUserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # tag = TagSerializer(many=True, read_only=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            for ingredient_json in ingredient_data:
                ingredient = Ingredient.objects.get(id=ingredient_json['id'])
                ing_in_recipe = IngredientInRecipe.objects.create(recipe=recipe,
                        ingredient=ingredient, amount=ingredient_json['amount'])
                print(ing_in_recipe)
        return recipe

    class Meta:
        model = Recipe
        fields = ['name', 'ingredients', 'author', 'cooking_timetime', 'text']
