from django.urls import include, path
from rest_framework import routers
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
