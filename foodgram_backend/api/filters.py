from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    '''Фильтрация названий ингредиентов.'''

    search_param = 'name'
