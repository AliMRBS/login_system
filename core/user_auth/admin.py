from django.contrib import admin
from .models import LoginAttempt
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'first_name', 'last_name', 'email'),
        }),
    )
    list_display = ('id', 'mobile', 'first_name', 'last_name', 'is_staff')
    search_fields = ('mobile', 'first_name', 'last_name', 'email')
    ordering = ('mobile',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'code', 'is_used')
    search_fields = ('mobile', 'code')
    list_filter = ('is_used',)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'ip_address', 'attempt_type', 'successful', 'is_blocked', 'block_until', 'created_at')
    list_filter = ('attempt_type', 'successful', 'is_blocked', 'created_at')
    search_fields = ('mobile', 'ip_address')
    ordering = ('-created_at',)
