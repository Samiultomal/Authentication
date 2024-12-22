from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'contact_number', 'is_approved', 'is_email_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_approved', 'is_email_verified', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'contact_number')
    ordering = ('created_at',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'contact_number', 'is_approved', 'is_email_verified')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'contact_number', 'is_approved', 'is_email_verified')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)