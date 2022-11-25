from django.contrib import admin
from users.models import CustomUser, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    """Кастомизация админ панели (управление подписками)."""
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)


admin.site.register(CustomUser)
admin.site.register(Subscription, SubscriptionAdmin)
