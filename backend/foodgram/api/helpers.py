from django.db.models import F, Sum
from recipes.models import AmountIngredient, Ingredient


def create_amount_ingredient(recipe, ingredients):
    objects = []
    for ingredient, amount in ingredients.values():
        objects.append(
            AmountIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
        )
    AmountIngredient.objects.bulk_create(objects)


def get_shoplist_ingredients(user):
    shoplist = [
        f'Список ингредиентов на покупку для \n\n{user.username}\n'
    ]
    ingredients = (
        Ingredient.objects.filter(recipe__recipe_in_shopping_cart__user=user)
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
