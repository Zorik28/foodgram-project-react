from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import CreateDestroyViewSet, User
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeObtainSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False)
    def subscriptions(self, request):
        user = get_object_or_404(User, id=request.user.id)
        queryset = get_list_or_404(User, followings__user=user)
        serializer = SubscriptionsSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'get':
            return RecipeObtainSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .select_related('ingredient', 'recipe')
            .prefetch_related('purchases')
            .filter(recipe__purchases__user=request.user)
            .values_list('ingredient__name', 'ingredient__measurement_unit')
            .annotate(Sum('amount'))
        )
        purchases = []
        for item in ingredients:
            purchases.append(f'{item[0]} - {item[2]} {item[1]}\n')
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=Purchases.txt'
        response.writelines(purchases)
        return response


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer


class SubscribeViewSet(CreateDestroyViewSet):
    serializer_class = SubscribeSerializer


class ShoppingCartModelViewSet(CreateDestroyViewSet):
    serializer_class = ShoppingCartSerializer
