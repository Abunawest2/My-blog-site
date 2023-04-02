from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('username','email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('email', 'username','first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    ordering = ['id']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BlogPost)
admin.site.register(Comment)