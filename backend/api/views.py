from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscribe

from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeObtainSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagSerializer)

User = get_user_model()


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
    serializer_class = RecipeCreateSerializer

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


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        get_object_or_404(
            Favorite, user=request.user, recipe=recipe_id
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        serializer.save(user=self.request.user, author=user)

    @action(methods=['delete'], detail=True)
    def delete(self, request, user_id):
        get_object_or_404(
            Subscribe, user=request.user, author=user_id
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ShoppingCartModelViewSet(ModelViewSet):
    serializer_class = ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe_id
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)