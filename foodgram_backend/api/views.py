from djoser import views
from recipes.models import Ingredient, Tag
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from users.models import User

from .serializers import IngredientSerializer, TagSerializer, UserSerializer


class UserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка тегов.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
