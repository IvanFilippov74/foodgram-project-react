from django.db.models import Exists
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import User
from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import TagSerializer
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer)
from .utils import delete, post, render_pdf


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class SubscribeView(APIView):
    '''Функционал создания и отмены, подписки на пользователя.'''

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        check = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
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
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'message': 'Вы не можете оформлять подписки на себя.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, user_id):
        follow = Follow.objects.filter(user=request.user, author=user_id)
        if not Follow.objects.filter(
            user=request.user, author=user_id
        ).exists():
            return Response(
                {'message': 'Вы не подписанны на этот профиль.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsList(ListAPIView):
    '''Представление списка подписок пользователя.'''

    permission_classes = (IsAuthenticated,)

    def get(self, request):
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
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewset(viewsets.ModelViewSet):
    '''Представление рецептов'''

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        params = self.request.query_params
        queryset = self.queryset
        if params:
            if 'is_favorited' in params:
                follow_bool = Recipe.objects.filter(
                    favorite__user=self.request.user
                )
                queryset = queryset.annotate(favorit=Exists(follow_bool))
            if 'is_in_shopping_cart' in params:
                shopping_bool = Recipe.objects.filter(
                    shopping__user=self.request.user
                )
                queryset = queryset.annotate(shoppings=Exists(shopping_bool))
        return queryset

    def get_permissions(self):
        if self.request.user.is_superuser:
            return (IsAdminOrReadOnly(),)
        return super().get_permissions()

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
        if request.method == 'POST':
            return post(
                request, pk, Recipe,
                FavoriteRecipe, SubscribeRecipeSerializer
            )
        if request.method == 'DELETE':
            return delete(request, pk, Recipe, FavoriteRecipe)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return post(
                request, pk, Recipe,
                ShoppingCart, SubscribeRecipeSerializer
            )
        if request.method == 'DELETE':
            return delete(request, pk, Recipe, ShoppingCart)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        return render_pdf(ingredients)
