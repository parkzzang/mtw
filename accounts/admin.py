from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "phone_number", "role", "is_staff", "is_active")
    ordering = ("-joined_at",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("기본 정보", {"fields": ("phone_number", "role", "is_verified", "is_phone_verified")}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("기록", {"fields": ("last_login", )}), 
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "phone_number", "role", "password1", "password2"),
        }),
    )
    readonly_fields = ("joined_at",)


admin.site.register(User, UserAdmin)