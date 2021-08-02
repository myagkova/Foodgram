# Generated by Django 3.0.5 on 2021-07-30 13:47

import colorfield.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0011_auto_20210728_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
            },
        ),
        migrations.RemoveField(
            model_name='favoriterecipes',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='favoriterecipes',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'verbose_name': 'Количество ингредиента в рецепте', 'verbose_name_plural': 'Количество ингредиентов в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterModelOptions(
            name='tagsinrecipe',
            options={'verbose_name': 'Тег рецепта', 'verbose_name_plural': 'Теги рецепта'},
        ),
        migrations.AlterField(
            model_name='follow',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор, на которого подписан'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to='recipes', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#ffffff', max_length=18, verbose_name='Цвет тега'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientinrecipe',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='ingredientinrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique-in-module'),
        ),
        migrations.DeleteModel(
            name='FavoriteRecipes',
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_favorited', to='api_v1.Recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipe_for_user', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
    ]