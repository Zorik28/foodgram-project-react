from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscribe, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('count_favourites',)
    inlines = [IngredientInRecipeInline]

    @admin.display(description='В избранном')
    def count_favourites(self, obj):
        return obj.favourites.count()


class ShoppinpCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppinpCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
