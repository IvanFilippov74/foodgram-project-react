from djoser.serializers import UserSerializer
from rest_framework import serializers
from recipes.models import Tag
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализация тегов.'''

    class Meta:
        model = Tag
        fields = '__all__'
