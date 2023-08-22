from api.validators import hex_color_validator
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, SET_NULL, CharField, DateTimeField,
                              ForeignKey, ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, TextField,
                              UniqueConstraint)
from PIL import Image

User = get_user_model()


class Ingredient(Model):
    name = CharField(
        verbose_name='Ингредиент',
        max_length=40,
    )
    measurement_unit = CharField(
        verbose_name='Единица измерения',
        max_length=40,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name} измеряется в {self.measurement_unit}'


class Tag(Model):
    name = CharField(
        verbose_name='Имя тэга',
        max_length=50,
        unique=True,
    )
    color = CharField(
        verbose_name='Цвет',
        max_length=15,
        unique=True,
        db_index=False,
    )
    slug = CharField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
        db_index=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'

    def clean(self):
        self.color = hex_color_validator(self.color)
        return super().clean()


class Recipe(Model):
    name = CharField(
        verbose_name='Название рецепта',
        max_length=80
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
        to=Ingredient,
        through='recipes.AmountIngredient',
    )
    text = TextField(
        verbose_name='Описание блюда',
        max_length=500,
    )
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        verbose_name='Тэг',
        related_name='recipes',
        to='Tag',
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=0,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail(256, 256)
        image.save(self.image.path)


class AmountIngredient(Model):
    recipe = ForeignKey(
        verbose_name='В каком используется рецепте',
        related_name='in_recipe',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredient = ForeignKey(
        verbose_name='Используемый ингредиент',
        related_name='ingredient_recipe',
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        default=0,
        validators=(
            MinValueValidator(
                1,
                'Нужен хотя бы 1 элемент.'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Несколько ингредиентов'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='\n%(app_label)s_%(class)s такая смесь '
                     'ингредиентов уже есть в базе.\n',
            ),
        )

    def __str__(self):
        return f'{self.amount} мерных единиц {self.ingredient}'


class ShoppingCart(Model):
    recipe = ForeignKey(
        verbose_name='Рецепты в корзине покупок',
        related_name='in_shopping_cart',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='shopping_cart',
        to=User,
        on_delete=CASCADE,
    )
    added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт на покупку'
        verbose_name_plural = 'Рецепты на покупку'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='\n%(app_label)s_%(class)s рецепт уже лежит '
                     'в корзине покупок.\n',
            ),
        )

    def __str__(self):
        return (f'{self.user.username} добавил(-ла) в корзину покупок: '
                f'{self.recipe}')


class Favourites(Model):
    recipe = ForeignKey(
        verbose_name='Любимые рецепты',
        related_name='in_favourites',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Пользователь',
        related_name='favourites',
        to=User,
        on_delete=CASCADE,
    )
    added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Избранное'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='\n%(app_label)s_%(class)s рецепт уже в избранном.\n',
            ),
        )

    def __str__(self):
        return f'{self.user.username} добавил(-ла) в избранное: {self.recipe}'
