from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'Юзер'),
    ('admin', 'Адинистратор'),
)


class CustomUser(AbstractUser):
    username = models.CharField('Логин', unique=True, max_length=150)
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        max_length=254
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    role = models.CharField(max_length=20, choices=ROLES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'