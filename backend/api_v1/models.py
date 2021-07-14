from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

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
    title = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    picture = models.ImageField(upload_to='recipes')
    text = models.TextField(
        verbose_name='Описание',
    )
    Ingredient = models.ForeignKey(
        to='Ingredient',
        related_name='ingredients',
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
    )
    Tag = models.ForeignKey(
        to='Tag',
        related_name='recipe_tag',
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    Time = models.TimeField(
        verbose_name='Время приготовления в минутах'
    )

    def __str__(self):
        return self.title


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
    amount = models.IntegerField(
        verbose_name='Количество'
    )
    units = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )
