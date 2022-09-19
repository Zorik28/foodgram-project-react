from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('count_favourites',)
    inlines = [IngredientInRecipeInline]

    @admin.display(description='В избранном')
    def count_favourites(self, obj):
        return obj.favourites.count()


class ShoppinpCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppinpCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)