from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from api.helpers import create_amount_ingredient
from api.validators import ingredient_validator, tag_validator
from recipes.models import Ingredient, Recipe, Tag

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
        read_only_fields = '__all__'


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
        return (
            user.following.filter(author=obj).exists()
            and not
            (user.is_anonymous or user == obj)
        )

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
    recipes = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

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
            'recipes_count',
        )
        read_only_fields = '__all__'

    def get_is_subscribed(self):
        return True

    def get_recipes_counted(self, obj):
        return obj.recipes.count()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'name',
            'color',
            'slug',
        )
        read_only_fields = '__all__'

    def validate(self, data):
        for key, value in data.items():
            data[key] = value.strip(' #').upper()
        return data


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit',
        )
        read_only_fields = '__all__'


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True, )
    author = UserSerializer(read_only=True, )
    ingredients = SerializerMethodField()
    is_favourite = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'tags',
            'text',
            'ingredients',
            'image',
            'cooking_time',
            'is_favourite',
            'is_in_shopping_cart',
        )
        read_only_fields = (
            'is_favourite',
            'is_in_shopping_cart',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.get(tags)
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

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favourite(self, recipe):
        user = self.context.get('view').request.user
        return (user.favourites.filter(recipe=recipe).exists()
                and not 
                user.is_anonymous
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        return (user.shopping_cart.filter(recipe=recipe).exists()
                and not
                user.is_anonymous
        )

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients = ingredient_validator(ingredients, Ingredient)
        data.update(
            {
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        tags = tag_validator(tags, Tag)
        data.update(
            {
                'tags': tags,
                'author': self.context.get('request').user,
            }
        )
        return data
