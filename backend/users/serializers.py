from djoser.serializers import UserSerializer
from recipes.models import Cart, Favorite, Recipe
from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)
from users.models import CustomUser, Subscription


class CustomUserSerializer(UserSerializer):
    """Сериализатор для эндпойнта /users/"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: CustomUser):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


class RecipeShortInfo(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionListSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortInfo(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortInfo(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Subscription.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        if data['author'] == data['user']:
            raise ValidationError({
                'errors': 'Ты не пожешь подписаться на себя.'
            })
        if Subscription.objects.filter(
                user=data['user'],
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Вы уже подписаны.'
            })
        return data

    def to_representation(self, instance):
        return SubscriptionListSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError({
                'errors': 'Уже есть в избранном.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(
            instance.recipe, context=context).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['recipe', 'user']
        model = Cart

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Cart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Данный рецепт уже есть в корзине.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(instance.recipe, context=context).data
