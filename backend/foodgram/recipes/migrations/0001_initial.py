# Generated by Django 4.2.4 on 2023-08-21 17:34

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AmountIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Нужен хотя бы 1 элемент.')], verbose_name='Количество ингредиента')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Несколько ингредиентов',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Favourites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Любимый рецепт',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(max_length=40, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Название рецепта')),
                ('text', models.TextField(max_length=500, verbose_name='Описание блюда')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('image', models.ImageField(upload_to='recipe_images/', verbose_name='Изображение блюда')),
                ('cooking_time', models.PositiveSmallIntegerField(default=0, verbose_name='Время приготовления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.AmountIngredient', to='recipes.ingredient', verbose_name='Ингредиенты в рецепте')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Имя тэга')),
                ('color', models.CharField(max_length=15, unique=True, verbose_name='Цвет')),
                ('slug', models.CharField(max_length=50, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_cart', to='recipes.recipe', verbose_name='Рецепты в корзине покупок')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Рецепт на покупку',
                'verbose_name_plural': 'Рецепты на покупку',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tag', verbose_name='Тэг'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_for_ingredient'),
        ),
        migrations.AddField(
            model_name='favourites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_favourites', to='recipes.recipe', verbose_name='Любимые рецепты'),
        ),
        migrations.AddField(
            model_name='favourites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='amountingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.ingredient', verbose_name='Используемый ингредиент'),
        ),
        migrations.AddField(
            model_name='amountingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_recipe', to='recipes.recipe', verbose_name='В каком используется рецепте'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='\nrecipes_shoppingcart рецепт уже лежит в корзине покупок.\n'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='unique_for_author'),
        ),
        migrations.AddConstraint(
            model_name='favourites',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='\nrecipes_favourites рецепт уже в избранном.\n'),
        ),
        migrations.AddConstraint(
            model_name='amountingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='\nrecipes_amountingredient такая смесь ингредиентов уже есть в базе.\n'),
        ),
    ]
