from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientSearchFilter, RecipeFilterSet
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.pagination import LimitPageNumberPagination
from api.serializers import (CreateRecipeSerializer, IngredientRecipe,
                                 IngredientSerializer, RecipeSerializer,
                                 TagSerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.serializers import CartSerializer, FavoriteSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    permission_classes = (IsAuthorOrAdminOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(model, user=user, recipe=recipe)
        model_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request, pk, serializers=CartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Cart)

    @action(
        methods=['GET'], permission_classes=[IsAuthenticated], detail=False
    )
    def download_shopping_cart(self, request):
        queryset = self.get_queryset()
        cart_objects = Cart.objects.filter(user=request.user)
        recipes = queryset.filter(cart__in=cart_objects)
        ingredients = IngredientRecipe.objects.filter(recipes__in=recipes)
        ing_types = Ingredient.objects.filter(
            ingredients_amount__in=ingredients
        ).annotate(total=Sum('ingredients_amount__amount'))

        lines = [f'{ing_type.name}, {ing_type.total}'
                 f' {ing_type.measurement_unit}' for ing_type in ing_types]
        filename = 'shopping_ingredients.txt'
        response_content = ''.join(lines)
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
