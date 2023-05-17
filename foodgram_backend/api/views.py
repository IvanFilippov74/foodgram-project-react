from django.http import FileResponse
from django.db.models import Exists
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import User
from .filters import RecipeFilter
from .mixins import ListViewSet
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          SubscribeUserSerializer, TagSerializer)
from .utils import delete, post, render_pdf


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class SubscribeView(APIView):
    '''Функционал создания и отмены, подписки на пользователя.'''

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        serializer = SubscribeUserSerializer(
            data={'user': request.user.id, 'author': user_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        follow = get_object_or_404(Follow, author=user_id, user=request.user)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsList(ListViewSet):
    '''Представление списка подписок пользователя.'''

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


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

    #permission_classes = [IsAuthorOrReadOnly | IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset.annotate(
            favorit=Exists(queryset),
            shoppings=Exists(queryset)
        )

    def get_permissions(self):
        if self.request.user.is_superuser:
            return (IsAdminOrReadOnly(),)
        return (IsAuthorOrReadOnly() or IsAuthenticatedOrReadOnly(),)

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
        return FileResponse(
            render_pdf(ingredients),
            as_attachment=True,
            filename='grocery_list.pdf',)
