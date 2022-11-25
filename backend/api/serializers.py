from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from rest_framework import serializers
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class TagListField(serializers.RelatedField):
    """ Сериализатор для получения списка тэгов"""

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Недопустимый первичный ключ "404" - объект не существует.'
            )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.SerializerMethodField(read_only=True)
    measurement_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def _get_ingredient(self, ingredient_id):
        return get_object_or_404(Ingredient, id=ingredient_id)

    def get_name(self, amount):
        return self._get_ingredient(amount.ingredient.id).name

    def get_measurement_unit(self, amount):
        return self._get_ingredient(amount.ingredient.id).measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()



class CreateRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания и обновления рецептов"""

    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    tags = TagListField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text',
                  'cooking_time')

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        return cooking_time


    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!')
        return tags

    def create_ingredients(self, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_amount, status = (
                IngredientRecipe.objects.get_or_create(**ingredient)
            )
            ingredients_list.append(ingredient_amount)
        return ingredients_list

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.ingredients.set(self.create_ingredients(ingredients))
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.ingredients.set(self.create_ingredients(ingredients))
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data