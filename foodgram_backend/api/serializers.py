from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import User


class CustomUserSerializer(UserSerializer):
    '''Сериализация пользователей.'''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj,
            user=self.context.get('request').user
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Сериализация новых пользователей.'''

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password'
        )


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


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    '''Сериализация игредиентов входящих в рецепты.'''

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    '''Сериализация списка рецептов.'''

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        try:
            if self.context.get('request').user.is_anonymous:
                return False
            return obj.favorit
        except AttributeError:
            return FavoriteRecipe.objects.filter(
                recipe=obj, user=self.context.get('request').user
            ).exists()
        except Exception:
            return False

    def get_is_in_shopping_cart(self, obj):
        try:
            if self.context.get('request').user.is_anonymous:
                return False
            return obj.shoppings
        except AttributeError:
            return ShoppingCart.objects.filter(
                recipe=obj, user=self.context.get('request').user
            ).exists()
        except Exception:
            False


class CreateIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов, для создания пользователем рецепта.'''

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта.'''

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        name = data.get('name')
        if len(name) > 200:
            raise serializers.ValidationError(
                {'name': 'Название рецепта превышает 200 символов.'}
            )
        ingredients = data.get('ingredients')
        ingredients_list = [ingredient.get('id') for ingredient in ingredients]
        for ingredient in ingredients:
            if ingredient.get('id') > Ingredient.objects.count():
                raise serializers.ValidationError(
                    {'ingredients': 'Такого ингредиента не существует.'}
                )
            if ingredients_list.count(ingredient['id']) > 1:
                duble = Ingredient.objects.get(
                    pk=ingredient.get('id')
                )
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент, {duble}, '
                                   f'выбран более одного раза.'
                })
        return data

    def create_ingredients(self, recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            create_ingredients = RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                amount=ingredient.get('amount'),
            )
            ingredients_list.append(create_ingredients)
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'tags' in validated_data:
            tags = validated_data.get('tags')
            instance.tags.set(tags)
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self.create_ingredients(
                instance, validated_data.get('ingredients')
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор отображения рецептов в подписке.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    '''Сериализатор отображения списка подписок.'''

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(author=obj.author, user=obj.user).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return SubscribeRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
