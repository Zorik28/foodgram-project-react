from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet
)

router = DefaultRouter()

router.register('users', CustomUserViewSet, 'user')
router.register('tags', TagViewSet, 'tag')
router.register('ingredients', IngredientViewSet, 'ingredient')
router.register('recipes', RecipeViewSet, 'recipe')

urlpatterns = [
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
    path('', include(router.urls)),
]
