from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

QUERY_SET_LENGTH = 15


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        help_text='Название ингредиента'
    )
    measure_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:QUERY_SET_LENGTH]


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        help_text='Название'
    )
    color = models.CharField(
        verbose_name='Цвет в формате HEX кода',
        max_length=7,
        unique=True,
        help_text='Цвет в формате HEX кода'
    )
    slug = models.SlugField(
        verbose_name='Slug адрес',
        max_length=200,
        unique=True,
        help_text='Slug адрес'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:QUERY_SET_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автора рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images',
        help_text='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Текст рецепта'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        help_text='Ингредиенты рецепта'
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes',
        help_text='Тег рецепта'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления минимум 1 минута'
            )
        ],
        help_text='Время приготовления'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:QUERY_SET_LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients',
        help_text='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное количество не меньше чем 1'
            )
        ],
        help_text='Количество'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
