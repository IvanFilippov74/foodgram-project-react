from djoser import views
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from recipes.models import Tag
from users.models import User


from .serializers import TagSerializer, UserSerializer


class UserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Предствление списка тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination
