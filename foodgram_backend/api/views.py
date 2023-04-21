from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,  # loc
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import User  # loc
from .filters import RecipeFilter  # loc
from .serializers import (CustomUserSerializer, IngredientSerializer,  # loc
                          RecipeCreateSerializer, RecipeListSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          TagSerializer)


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

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
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Представление списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewset(viewsets.ModelViewSet):
    '''Представление рецептов'''

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        grocery_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        pdfmetrics.registerFont(
            TTFont('verdana', 'fonts/verdana.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="grocery_list.pdf"')
        for ingredient in ingredients:
            if ingredient[0] not in grocery_list:
                grocery_list[ingredient[0]] = {
                    'measurement_unit': ingredient[1],
                    'amount': ingredient[2]
                }
            else:
                grocery_list[ingredient[0]]['amount'] += ingredient[2]
        report = canvas.Canvas(response)
        report.setFont('verdana', 22)
        report.drawString(20, 800, 'Мой список покупок:')
        height = 770
        report.setFont('verdana', 14)
        for i, (name, data) in enumerate(grocery_list.items(), 1):
            report.drawString(40, height, (f'{i}. {name.capitalize()} - '
                                           f'{data["amount"]} '
                                           f'{data["measurement_unit"]}'))
            height -= 30
        report.setFont('verdana', 16)
        report.setFillColorRGB(0.25, 0.25, 0.25)
        report.drawCentredString(
            300, 30, 'Foodgram - Ваш продуктовый помощник.'
        )
        report.showPage()
        report.save()
        return response
