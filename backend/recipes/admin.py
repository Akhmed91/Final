from django.contrib import admin

from .models import Favorite, Ingredient, IngredientRecipe, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('^name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorited')
    list_filter = ('author', 'name', 'tags')

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')



class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientRecipe)
