from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import (CustomUser, Ingredient, IngredientInRecipe, FavoriteRecipes,
                     Recipe, Tag, TagsInRecipe)
import logging
from rest_framework.generics import get_object_or_404

logging.basicConfig(level=logging.INFO)


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField('get_email')
    id = serializers.SerializerMethodField('get_id')
    username = serializers.SerializerMethodField('get_username')
    first_name = serializers.SerializerMethodField('get_first_name')
    last_name = serializers.SerializerMethodField('get_last_name')

    def get_email(self, obj):
        return obj.email

    def get_id(self, obj):
        return obj.id

    def get_username(self, obj):
        return obj.username

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    class Meta:
        model = CustomUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_ingredient_id')
    name = serializers.SerializerMethodField('get_ingredient_name')
    measurement_unit = serializers.SerializerMethodField(
        'get_ingredient_measurement_unit')

    def get_ingredient_id(self, obj):
        return obj.ingredient.id

    def get_ingredient_name(self, obj):
        return obj.ingredient.title

    def get_ingredient_measurement_unit(self, obj):
        return obj.ingredient.units

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'amount', 'measurement_unit']


class TagsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_tag_id')
    name = serializers.SerializerMethodField('get_tag_name')
    color = serializers.SerializerMethodField('get_tag_color')
    slug = serializers.SerializerMethodField('get_tag_slug')

    def get_tag_id(self, obj):
        return obj.tag.id

    def get_tag_name(self, obj):
        return obj.tag.title

    def get_tag_color(self, obj):
        return obj.tag.color

    def get_tag_slug(self, obj):
        return obj.tag.slug

    class Meta:
        model = TagsInRecipe
        fields = ['id', 'name', 'color', 'slug']


# class FavoriteRecipesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FavoriteRecipes
#         fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagsInRecipeSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='conversion_bool')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_json in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_json['id'])
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_json['amount']
            )
        for tag_ in tags_data:
            tag = Tag.objects.get(id=tag_)
            TagsInRecipe.objects.create(recipe=recipe, tag=tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        print(ingredients_data)

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('name', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        IngredientInRecipe.objects.filter(recipe=instance).delete()
        TagsInRecipe.objects.filter(recipe=instance).delete()
        for ingredient_json in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_json['id'])
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_json['amount']
            )

        for tag_ in tags_data:
            tag = Tag.objects.get(id=tag_)
            TagsInRecipe.objects.create(recipe=instance, tag=tag)

        instance.save()
        return instance

    def conversion_bool(self, obj):
        user=self.context["request"].user
        try:
            FavoriteRecipes.objects.get(user=user, recipe=obj)
            return True
        except FavoriteRecipes.DoesNotExist:
            return False

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'name', 'ingredients', 'author', 'image',
                   'is_favorited', 'cooking_time', 'text']
