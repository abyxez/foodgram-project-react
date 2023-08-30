from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, TextField,
                              UniqueConstraint)
from PIL import Image

from api.validators import hex_color_validator

User = get_user_model()


class Ingredient(Model):
    name = CharField(
        'Ингредиент',
        max_length=40,
    )
    measurement_unit = CharField(
        'Единица измерения',
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
        'Имя тэга',
        max_length=50,
        unique=True,
    )
    color = CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета. '
                        'Например, красный: #FF0000. '
            )
        ],
    )
    slug = CharField(
        'Слаг',
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'

    def clean_color(self):
        self.color = hex_color_validator(self.color)
        return super().clean()


class Recipe(Model):
    name = CharField(
        'Название рецепта',
        max_length=80
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
        to=Ingredient,
        through='recipes.AmountIngredient',
    )
    text = TextField(
        'Описание блюда',
        max_length=500,
    )
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=CASCADE,
        null=False,
        blank=False
    )
    tags = ManyToManyField(
        verbose_name='Тэг',
        related_name='recipes',
        to='Tag',
    )
    pub_date = DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        'Изображение блюда',
        upload_to='recipe_images/',
    )
    cooking_time = PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(5),
            MaxValueValidator(360),
        )
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
        'Количество ингредиента',
        validators=(
            MinValueValidator(
                1,
                'Нужен хотя бы 1 элемент.'
            ),
            MaxValueValidator(
                40,
                'Слишком много ингредиентов.'
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


class BaseRecipeUserModel(Model):
    """
    Специальный класс, предотвращающий
    дублирование схожего кода.
    """

    added = DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        abstract = True


class ShoppingCart(BaseRecipeUserModel):
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


class Favourites(BaseRecipeUserModel):
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
