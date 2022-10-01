from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField, ModelSerializer, PrimaryKeyRelatedField,
    SerializerMethodField, StringRelatedField, ValidationError
)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)
from users.models import Subscribe
from .mixins import CreatePopItems, IsSubscribed, RepresentationMixin

User = get_user_model()


class CustomUserSerializer(UserSerializer, IsSubscribed):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeObtainSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = StringRelatedField(source='ingredient.name')
    measurement_unit = StringRelatedField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeObtainSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeObtainSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class IngredientInRecipeCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeCreateSerializer(RepresentationMixin, CreatePopItems):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        unique_ingredients = []
        for ingredient in data.get('ingredients'):
            if ingredient['id'] in unique_ingredients:
                raise ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться'
                })
            unique_ingredients.append(ingredient['id'])

        tags = data.get('tags')
        if not tags:
            raise ValidationError({'tags': 'Выберите тэг'})
        unique_tags = []
        for tag in tags:
            if tag in unique_tags:
                raise ValidationError({'tags': 'Тэги должны быть уникальными'})
            unique_tags.append(tag)
        return data

    def create(self, validated_data):
        tags, ingredients = self.pop_items(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        self.create_tags(recipe, tags)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        tags, ingredients = self.pop_items(validated_data)
        self.create_ingredients(recipe, ingredients)
        self.create_tags(recipe, tags)
        return super().update(recipe, validated_data)


class RecipeSerializer(ModelSerializer):
    """Сериализатор для получения ограниченной версии модели Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(RepresentationMixin):

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, data):
        user = self.context.get('request').user
        author = data.get('author')
        if user == author:
            raise ValidationError('Невозможно подписаться на себя')
        return data


class SubscriptionsSerializer(ModelSerializer, IsSubscribed):
    """Сериализатор для отображения подписок."""

    is_subscribed = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)
    recipes_count = IntegerField(source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeSerializer(queryset, many=True).data


class FavoriteSerializer(RepresentationMixin):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в избранном'
            )
        ]


class ShoppingCartSerializer(RepresentationMixin):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в избранном'
            )
        ]
