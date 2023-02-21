from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('id', 'name', 'author', 'pub_date', )
    list_filter = ('author__username', 'name', 'tags')
    search_fields = ('author__username', 'name', 'tags__name',)
    empty_value_display = '-пустые поля-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    search_fields = ('name',)









