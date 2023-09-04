from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
    )
    fields = (
        (
            'username',
            'email',
        ),
        (
            'first_name',
            'last_name',
        ),
        ('is_active', ),
    )
    fieldsets = []

    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'first_name',
        'email',
        'is_active',
    )
