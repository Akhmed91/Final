from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from api.permissions import IsAuthorOrAdminOrReadOnly
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser, Subscription
from api.pagination import LimitPageNumberPagination
from users.serializers import (CustomUserSerializer,
                               SubscriptionListSerializer,
                               SubscriptionSerializer)


class UserViewSet(UserViewSet):
    """Представление для эндпойнта /users/"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        subscriptions_list = self.paginate_queryset(
            CustomUser.objects.filter(following__user=request.user)
        )
        serializer = SubscriptionListSerializer(
            subscriptions_list, many=True, context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        if request.method != 'POST':
            subscription = get_object_or_404(
                Subscription,
                author=get_object_or_404(CustomUser, id=id),
                user=request.user
            )
            self.perform_destroy(subscription)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscriptionSerializer(
            data={
                'user': request.user.id,
                'author': get_object_or_404(CustomUser, id=id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
