from rest_framework import serializers
from .models import (CustomUser, Follow, Ingredient, IngredientInRecipe,
                     FavoriteRecipes, ShoppingCart, Recipe, Tag, TagsInRecipe)
import logging
from rest_framework.validators import UniqueTogetherValidator
from django.core.files.base import ContentFile
import base64
import six
import uuid
import imghdr
from django.contrib.auth.models import AnonymousUser

logging.basicConfig(level=logging.INFO)


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField('get_email')
    id = serializers.SerializerMethodField('get_id')
    username = serializers.SerializerMethodField('get_username')
    first_name = serializers.SerializerMethodField('get_first_name')
    last_name = serializers.SerializerMethodField('get_last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscription')

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

    def get_subscription(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        try:
            Follow.objects.get(user=user, following=obj)
            return True
        except Follow.DoesNotExist:
            return False

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
    id = serializers.SerializerMethodField('get_ingredient_id')
    name = serializers.SerializerMethodField('get_ingredient_name')
    measurement_unit = serializers.SerializerMethodField(
        'get_ingredient_measurement_unit')

    def get_ingredient_id(self, obj):
        return obj.ingredient.id

    def get_ingredient_name(self, obj):
        return obj.ingredient.name

    def get_ingredient_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

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
        return obj.tag.name

    def get_tag_color(self, obj):
        return obj.tag.color

    def get_tag_slug(self, obj):
        return obj.tag.slug

    class Meta:
        model = TagsInRecipe
        fields = ['id', 'name', 'color', 'slug']


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension,)
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagsInRecipeSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='conversion_bool')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='is_recipe_in_shopping_cart')
    image = Base64ImageField(max_length=None, use_url=True)

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
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        try:
            FavoriteRecipes.objects.get(user=user, recipe=obj)
            return True
        except FavoriteRecipes.DoesNotExist:
            return False

    def is_recipe_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        try:
            ShoppingCart.objects.get(user=user, recipe=obj)
            return True
        except ShoppingCart.DoesNotExist:
            return False

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
        try:
            Follow.objects.get(user=user, following=obj)
            return True
        except Follow.DoesNotExist:
            return False

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
        raise serializers.ValidationError("Нельзя подписаться на самого себя")
