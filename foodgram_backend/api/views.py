from djoser import views
from rest_framework.pagination import PageNumberPagination
from users.models import User

from .serializers import UserSerializer


class UserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
