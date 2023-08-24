from django.contrib.admin import ModelAdmin, TabularInline, register, site
from django.utils.safestring import mark_safe

from recipes.forms import TagForm
from recipes.models import (AmountIngredient, Favourites, Ingredient, Recipe,
                            ShoppingCart, Tag)

EMPTY_VALUE_DISPLAY = '-empty-'
site.site_header = 'Foodgram Admin panel'


class IngredientInline(TabularInline):
    model = AmountIngredient
    extra = 2


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

    save_on_top = True
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

    save_on_top = True
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
    raw_id_fields = ('author', )
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
    save_on_top = True
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
