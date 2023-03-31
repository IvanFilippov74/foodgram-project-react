from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,  # loc
                            ShoppingCart, Tag)
from users.models import User  # loc
from .serializers import (CustomUserSerializer, IngredientSerializer,  # loc
                          RecipeCreateSerializer, RecipeListSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          TagSerializer)


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=request.user, author=author)
        check = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
        if request.method == 'POST':
            if author != request.user and not check:
                subscribes = Follow.objects.create(
                    user=request.user, author=author
                )
                serializer = SubscribeSerializer(
                    subscribes, context={request: 'request'}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            if check:
                return Response(
                    {'message': 'Вы уже подписаны на данного пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'message': 'Вы не можете оформлять подписки на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            if not check:
                return Response(
                    {'message': 'Вы не подписанны на этот профиль.'}
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscribes = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            pages, many=True, context={request: 'request'}
        )
        return self.get_paginated_response(serializer.data)


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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        get_favorite = FavoriteRecipe.objects.filter(
            recipe=recipe, user=request.user
        )
        check = FavoriteRecipe.objects.filter(
            recipe=recipe, user=request.user
        ).exists()
        if request.method == 'POST':
            if check:
                return Response(
                    {'message':
                        f'Вы уже добавили рецепт {recipe} в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeRecipeSerializer(
                recipe, context={request: 'request'}
            )
            FavoriteRecipe.objects.create(
                recipe=recipe, user=request.user
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not check:
                return Response(
                    {'message':
                        f'Вы не добавляли рецепт {recipe} в избранное.'}
                )
            get_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        get_shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user
        )
        check = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user
        ).exists()
        if request.method == 'POST':
            if check:
                return Response(
                    {'message':
                        f'Вы уже добавили рецепт {recipe} в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeRecipeSerializer(
                recipe, context={request: 'request'}
            )
            ShoppingCart.objects.create(
                recipe=recipe, user=request.user
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not check:
                return Response(
                    {'message':
                        f'Вы не добавляли рецепт {recipe} в список покупок.'}
                )
            get_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
