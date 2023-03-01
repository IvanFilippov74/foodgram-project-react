from djoser import views
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from recipes.models import Ingredient, Recipe, Tag  # loc
from users.models import User  # loc
from .serializers import (CustomUserSerializer, IngredientSerializer,  # loc
                          RecipeListSerializer, TagSerializer)


class UserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка тегов.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewset(viewsets.ModelViewSet):
    '''Представление рецептов'''

    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
