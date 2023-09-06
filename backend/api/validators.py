from string import hexdigits
from http import HTTPStatus

from django.core.exceptions import ValidationError
from django.utils import deconstruct


def ingredient_validator(ingredients, Ingredient):
    if not ingredients:
        raise ValidationError('Не указаны ингридиенты')

    valid_ingredients = {}

    for ingredient in ingredients:
        valid_ingredients[ingredient['id']] = int(ingredient['amount'])

        if valid_ingredients[ingredient['id']] <= 0:
            raise ValidationError(
                'Количество каждого ингредиента '
                'не может быть меньше 1. '
            )
        if valid_ingredients[ingredient['id']] > 1000:
            raise ValidationError(
                'Вы пытаетесь добавить слишком '
                'большое количество ингредиентов. '
            )
    ingredients_to_add = Ingredient.objects.filter(
        id__in=valid_ingredients.keys()
    )

    for ingredient in ingredients_to_add:
        valid_ingredients[ingredient.id] = (
            ingredient,
            valid_ingredients[ingredient.id]
        )

    return valid_ingredients


@deconstruct.deconstructible
class MinLenValidator:
    min_len = 0
    field = 'Полученное значение'
    error_message = '\n%s слишком короткое значение.\n'

    def __init__(self, min_len, field, error_message: str | None = None):
        if min_len is not None:
            self.min_len = min_len
        if field is not None:
            self.field = field
        if error_message is not None:
            self.error_message = error_message
        else:
            self.error_message = self.error_message % field

    def __call__(self, value):
        if len(value) < self.min_len:
            raise ValidationError(self.error_message)


def tag_validator(tags_ids, Tag):
    if not tags_ids:
        raise ValidationError(
            'Не указаны тэги.'
        )
    tags = Tag.objects.filter(id__in=tags_ids)

    if len(tags) != len(tags_ids):
        raise ValidationError(
            'Указан несуществующий тэг.'
        )
    return tags


def hex_color_validator(color):
    color = color.strip('#').upper()
    if len(color) not in (3, 6):
        raise ValidationError(
            f'Код цвета {color} неверной длины: {len(color)}.'
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(
            f'Значение {color} не является шестнадцатеричным.'
        )
    if len(color) == 3:
        return f'#{color[0] * 2}{color[1] * 2}{color[2] * 2}'.upper()
    return '#' + color.upper()
