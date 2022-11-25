from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser


class Ingredient(models.Model):
    """Модель Ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэгов рецептов."""

    name = models.CharField(
        verbose_name='Название тэга',
        max_length=200,
        db_index=True
        )
    color = models.CharField(
        verbose_name='Цвет тэга',
        help_text='Цвет в формате HEX: #E26C2D',
        max_length=10,
        unique=True,
        )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=200,
        unique=True,
        )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(
        max_length=1000,
        verbose_name='Описание'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    ingredients = models.ManyToManyField(
        'IngredientRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes',
        )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
        )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Недопустимое значение, меньше 1 мин.'
            )
        ],
        verbose_name='Время приготовления'
    )
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients_amount',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        default=0,
        validators=(MinValueValidator(
            1, 'Слишком малое количество ингредиента.'
            ),),)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorites',
            ),
        )


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='cart',
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Корзина рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart',
            ),
        )
