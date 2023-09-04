from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.helpers import get_shoplist_ingredients
from api.mixins import CreateDeleteViewMixin
from api.paginators import PageLimitPagination
from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             TagSerializer, UserRecipeSerializer,
                             UserSubscribeSerializer)
from recipes.models import Favourites, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions

User = get_user_model()


class UserViewSet(UserViewSet, CreateDeleteViewMixin):
    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions, )
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        return author

    @subscribe.mapping.post
    def create_subscribe(self, request, id):
        return self.create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        return self.delete_relation(Q(author__id=id))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(following__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None


class RecipeViewSet(ModelViewSet, CreateDeleteViewMixin):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly, )
    pagination_class = PageLimitPagination
    add_serializer = UserRecipeSerializer

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if self.request.user.is_anonymous:
            return queryset
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if shopping_cart:
            queryset = queryset.filter(
                in_shopping_cart__user=self.request.user
            )
        favourites = self.request.query_params.get('is_favourite')
        if favourites:
            queryset = queryset.filter(in_favourites__user=self.request.user)
        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def make_favourite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        return recipe

    @make_favourite.mapping.post
    def recipe_into_favourites(self, request, id):
        self.link_model = Favourites
        return self.create_relation(id)

    @make_favourite.mapping.delete
    def recipe_out_of_favourites(self, request, id):
        self.link_model = Favourites
        return self.delete_relation(Q(recipe__id=id))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def into_shopping_cart(self, request, id):
        if request.method == 'POST':
            return self.recipe_into_shopping_cart(ShoppingCart, request.user, id)
        else:
            return self.recipe_out_of_shopping_cart(ShoppingCart, request.user, id)

    @into_shopping_cart.mapping.post
    def recipe_into_shopping_cart(self, request, id):
        self.link_model = ShoppingCart
        return self.create_relation(id)

    @into_shopping_cart.mapping.delete
    def recipe_out_of_shopping_cart(self, request, id):
        self.link_model = ShoppingCart
        return self.delete_relation(Q(recipe__id=id))

    @action(methods='get', detail=False)
    def get_shopping_cart_txt(self, request, id):
        user = self.request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        name = f'{user.username}_id{user.id}_shoplist.txt'
        shoplist = get_shoplist_ingredients(user)
        response = HttpResponse(shoplist)
        response['Content-Disposition'] = f'attachment; filename={name}'
        return response


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None