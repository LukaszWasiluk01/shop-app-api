from core.models import Category, Product, User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class UserAdmin(UserAdmin):
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")}),)


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Category)
