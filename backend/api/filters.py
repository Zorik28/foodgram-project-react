from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters as f
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = f.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = f.BooleanFilter(method='filter_is_in_shopping_cart')
    tags = f.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(favourites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            queryset
        return queryset.filter(purchases__user=self.request.user)
