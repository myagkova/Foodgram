from django.utils import timezone

from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db.models import ForeignKey


class CustomUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'username']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Recipe(models.Model):
    author = models.ForeignKey(
        to='CustomUser',
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes',
        null=True
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Tag(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега'
    )
    color = ColorField(default='#ffffff')
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега(английский)'
    )


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название продукта'

    )
    units = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        to='Ingredient',
        max_length=200,
        on_delete=models.CASCADE, blank=True,
        verbose_name='Название продукта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = verbose_name
        unique_together = ['ingredient', 'recipe']

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class TagsInRecipe(models.Model):
    tag = models.ForeignKey(
        to='Tag',
        max_length=200,
        on_delete=models.CASCADE, blank=True,
        verbose_name='Название тега'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Рецепт'
    )


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipe_for_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="follower"
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_following"
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='purchases', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='customers', verbose_name='Покупка')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
