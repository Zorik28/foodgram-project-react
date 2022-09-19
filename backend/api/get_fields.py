from recipes.models import IngredientInRecipe
from users.models import Subscribe


def is_subscribed(self, obj):
    request = self.context.get('request')
    if request is None or request.user.is_anonymous:
        return False
    return Subscribe.objects.filter(
        user=request.user, author=obj.id
    ).exists()


def get_items(recipe, ingredients, tags):
    IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ])
    for tag in tags:
        recipe.tags.add(tag)


def pop_items(validated_data):
    tags = validated_data.pop('tags')
    ingredients = validated_data.pop('ingredients')
    return tags, ingredients
