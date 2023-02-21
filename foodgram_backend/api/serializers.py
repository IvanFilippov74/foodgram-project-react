from djoser.serializers import UserSerializer
from recipes.models import Ingredient, Tag
from rest_framework import serializers
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


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализация ингредиентов.'''
    
    class Meta:
        model = Ingredient
        fields = '__all__'
