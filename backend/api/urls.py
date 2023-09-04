from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'api'

router = DefaultRouter()

router.register(r'users', UserViewSet, 'users')
router.register(r'ingredients', IngredientViewSet, 'ingredients')
router.register(r'recipes', RecipeViewSet, 'recipes')
router.register(r'tags', TagViewSet, 'tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
