from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        StringRelatedField, ValidationError)
from users.models import Subscribe

from .get_fields import get_items, is_subscribed, pop_items

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)


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
    amount = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeCreateSerializer(ModelSerializer):
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

        if not data.get('tags'):
            raise ValidationError({'tags': 'Выберите тэг'})
        return data

    def create(self, validated_data):
        tags, ingredients = pop_items(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        get_items(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        tags, ingredients = pop_items(validated_data)
        get_items(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeObtainSerializer(instance=instance, context=context).data


class FavoriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source='recipe.id', read_only=True)
    name = StringRelatedField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = IntegerField(source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsRecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)
    recipes_count = IntegerField(source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Recipe.objects.filter(author=obj)
        return SubscriptionsRecipeSerializer(queryset, many=True).data


class SubscribeSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(source='id', read_only=True)
    author = PrimaryKeyRelatedField(source='id', read_only=True)

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return SubscriptionsSerializer(instance.author, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
