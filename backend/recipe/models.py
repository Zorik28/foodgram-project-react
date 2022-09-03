from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    colour = models.CharField(max_length=200, unique=True, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Относительный URL')

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Aвтор',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Ссылка на картинку')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (минуты)'
    )

    def __str__(self) -> str:
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(verbose_name='Количество, кг')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='purchases',
        verbose_name='Покупатель',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='purchases',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favourites',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favourites',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='followings',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
