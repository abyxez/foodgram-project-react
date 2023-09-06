from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import status

from api.helpers import create_amount_ingredient
from api.validators import ingredient_validator, tag_validator
from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class UserRecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'image',
        )
        read_only_fields = ('__all__', )


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.following.filter(author=obj).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_counted = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_counted',
        )
        read_only_fields = ('__all__', )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    # def validate(self, data):
    #     author = self.instance
    #     user = self.context.get('request').user
    #     if Subscriptions.objects.filter(author=author, user=user).exists():
    #         raise ValidationError(
    #             detail='Вы уже подписаны на этого пользователя!',
    #             code=status.HTTP_400_BAD_REQUEST
    #         )
    #     if user == author:
    #         raise ValidationError(
    #             detail='Вы не можете подписаться на самого себя!',
    #             code=status.HTTP_400_BAD_REQUEST
    #         )
    #     return data
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = UserRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_counted(self, obj):
        return obj.recipes.count()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = ('__all__', )

    def validate_color(self, data):
        color = data.get('color')
        validate_color = color.strip('#').upper()
        if Tag.objects.filter(color=color).exists():
            raise ValidationError(
                'Такой тэг уже есть в базе данных.'
            )
        else:
            Tag.objects.get_or_create(
                name=data['name'],
                color=validate_color,
                slug=data['slug'],
            )
        return data


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = ('__all__', )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True, )
    author = UserSerializer(read_only=True, )
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'ingredients',
            'tags',
            'cooking_time',
            'text',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredient_recipe__amount'),
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False

        return user.favourites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False

        return user.shopping_cart.filter(recipe=recipe).exists()

    def validate(self, data):
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        name = self.initial_data.get('name')

        if Recipe.objects.filter(
            author=self.context.get('request').user,
            name=name
            ).exists():
            raise ValidationError(
                'Рецепт с таким названием уже '
                'был создан ранее. '
            )
        
        tags = tag_validator(tags_ids, Tag)
        ingredients = ingredient_validator(ingredients, Ingredient)
        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
                'name': name,
            }
        )
        return data
        
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_amount_ingredient(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            create_amount_ingredient(recipe, ingredients)

        recipe.save()
        return recipe
