from string import hexdigits
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils import deconstruct

if TYPE_CHECKING:
    from recipes.models import Ingredient, Tag


def ingredient_validator(ingredients):
    if not ingredients:
        raise ValidationError(
            'Не указаны ингредиенты.'
        )
    valid_ingredients = []
    for ingredient in ingredients:
        if ingredient.get('amount') <= 0:
            raise ValidationError(
                'Количество каждого ингредиента '
                'не может быть меньше 1. '
            )
        valid_ingredients.append(ingredient.get('id'))
    if len(set(valid_ingredients)) != len(valid_ingredients):
        raise ValidationError(
            'Вы пытаетесь добавить два одинаковых ингредиента. '
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


def tag_validator(tags_ids):
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
    color = color.strip(' #')
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
