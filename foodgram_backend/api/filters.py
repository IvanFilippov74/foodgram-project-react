from django_filters import rest_framework as filter

from recipes.models import Recipe
from users.models import User

STATUS_CHOICES = (
    (0, 'false',),
    (1, 'true',),
)


class RecipeFilter(filter.FilterSet):
    '''Фильтры для сортировки рецептов.'''
    tags = filter.AllValuesMultipleFilter(field_name='tags__slug')
    author = filter.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filter.ChoiceFilter(
        choices=STATUS_CHOICES, method='filter_is_favorited')
    is_in_shopping_cart = filter.ChoiceFilter(
        choices=STATUS_CHOICES, method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
