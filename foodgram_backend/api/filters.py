from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient


class IngredientSearchFilter(FilterSet):
    '''Фильтрация названий ингредиентов.'''

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
