from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from.fields import Base64ImageField
from .models import (CustomUser, FavoriteRecipe, Follow, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingCart, Tag,
                     TagsInRecipe)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscription')

    def get_subscription(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

    class Meta:
        model = CustomUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True, source=
                                             'ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'amount', 'measurement_unit']


class TagsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.CharField(read_only=True, source='tag.name')
    color = serializers.CharField(read_only=True, source='tag.color')
    slug = serializers.CharField(read_only=True, source='tag.slug')

    class Meta:
        model = TagsInRecipe
        fields = ['id', 'name', 'color', 'slug']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagsInRecipeSerializer(many=True, read_only=True)
    cooking_time = serializers.IntegerField(error_messages={
            'invalid': 'Время приготовления должно быть в формате целого числа'
        })
    is_favorited = serializers.SerializerMethodField(
        method_name='conversion_bool')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='is_recipe_in_shopping_cart')
    image = Base64ImageField(max_length=None, use_url=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        for ingredient in ingredients_data:
            if ingredient['amount'] < 0:
                raise serializers.ValueError(
                    'Введите целое число больше 0 для количества ингредиента')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_json in ingredients_data:
            ingredient = get_object_or_404(Ingredient, id=ingredient_json['id'])
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_json['amount']
            )
        for tag_ in tags_data:
            tag = get_object_or_404(Tag, id=tag_)
            TagsInRecipe.objects.create(recipe=recipe, tag=tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        IngredientInRecipe.objects.filter(recipe=instance).delete()
        TagsInRecipe.objects.filter(recipe=instance).delete()
        for ingredient_json in ingredients_data:
            ingredient = get_object_or_404(Ingredient, id=ingredient_json['id'])
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_json['amount']
            )

        for tag_ in tags_data:
            tag = get_object_or_404(Tag, id=tag_)
            TagsInRecipe.objects.create(recipe=instance, tag=tag)

        instance.save()
        return instance

    def validate_cooking_time(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Введите целое число больше 0 для времени приготовления'
            )
        return data

    def conversion_bool(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def is_recipe_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'name', 'ingredients', 'author', 'image',
                  'is_favorited', 'is_in_shopping_cart', 'cooking_time', 'text']


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='is_user_subscribed')
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    def is_user_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, following=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']
        model = CustomUser
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['following', 'user']
            )
        ]

    def validate(self, data):
        if self.context['request'].user != data['following']:
            return data
        raise serializers.ValidationError('Нельзя подписаться на самого себя')
