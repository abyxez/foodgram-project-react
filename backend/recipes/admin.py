from django.contrib.admin import ModelAdmin, TabularInline, register, site
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from recipes.forms import AmountIngredientFormSet, TagForm
from recipes.models import (AmountIngredient, Favourites, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscriptions

EMPTY_VALUE_DISPLAY = '-empty-'
site.site_header = 'Foodgram Admin panel'


User = get_user_model()


class IngredientInline(TabularInline):
    model = AmountIngredient
    extra = 0
    formset = AmountIngredientFormSet


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = (
        'name',
        'slug',
        'color'
    )
    search_fields = (
        'name',
        'color',
    )
    empty_value_display = EMPTY_VALUE_DISPLAY


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    empty_value_display = EMPTY_VALUE_DISPLAY


@register(AmountIngredient)
class LinksAdmin(ModelAdmin):
    pass


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'author',
        'get_image',
        'count_favourites',
    )
    fields = (
        (
            'name',
            'cooking_time',
        ),
        (
            'author',
            'tags',
        ),
        (
            'text',
        ),
        (
            'image',
        ),
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name',
    )
    list_filter = (
        'name',
        'author__username',
        'tags__name',
    )

    inlines = (IngredientInline, )
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="30" ')

    get_image.short_description = 'Изображение'

    def count_favourites(self, obj):
        return obj.in_favourites.count()

    count_favourites.short_description = 'В избранном'


@register(Favourites)
class FavouriteAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
        'added',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
        'added',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )


@register(Subscriptions)
class SubscriptionsAdmin(ModelAdmin):
    list_display = (
        'author',
        'added',
    )
    search_fields = (
        'author__username',
    )
    list_filter = (
        'author__username',
    )
