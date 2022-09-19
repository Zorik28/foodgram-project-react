from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscribeViewSet,
                    TagViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorites'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_carts'
)
router.register('users', CustomUserViewSet)
router.register(
    r'users/(?P<author_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribes'
)


urlpatterns = [
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
    path('', include(router.urls)),
]
