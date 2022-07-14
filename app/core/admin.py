from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User, Product, Category


class UserAdmin(UserAdmin):
    add_fieldsets = ((
        None,
        {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
        )


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Category)
