from django.db.models import F, Sum
from django.apps import apps

from recipes.models import AmountIngredient


def create_amount_ingredient(recipe, ingredients):
    ingredient_list = []

    for ingredient, amount in ingredients.values():
        ingredient_list.append(
            AmountIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )
        )
    AmountIngredient.objects.bulk_create(ingredient_list)


def get_shoplist_ingredients(user):
    shoplist = [
        f'Список ингредиентов на покупку для \n\n{user.username}\n'
    ]
    Ingredient = apps.get_model('recipes', 'Ingredient')
    ingredients = (
        Ingredient.objects.filter(recipes__recipe_in_shopping_cart__user=user)
        .values('name', measurement=F('measurement_unit'))
        .annotate(amount=Sum('recipe__amount'))
    )
    ingredient_list = [
        f'{ingredient["name"]}: '
        f'{ingredient["amount"]} {ingredient["measurement"]}'
        for ingredient in ingredients
    ]
    shoplist.extend(ingredient_list)
    return '\n'.join(shoplist)
