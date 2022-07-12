from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    add_fieldsets = ((
        None,
        {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
        )


admin.site.register(User, UserAdmin)
