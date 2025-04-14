from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "phone_number", "role", 
        "is_verified", "is_phone_verified", 
        "is_staff", "is_active"
    )
    ordering = ("-joined_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("기본 정보", {
            "fields": (
                "phone_number", "role", 
                "is_verified", "is_phone_verified", 
                "license_image"
            )
        }),
        ("권한", {
            "fields": (
                "is_active", "is_staff", "is_superuser", 
                "groups", "user_permissions"
            )
        }),
        ("기록", {"fields": ("last_login", "joined_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "phone_number", 
                "role", "password1", "password2"
            ),
        }),
    )

    list_filter = ("role", "is_verified", "is_phone_verified", "is_staff")

    search_fields = ("username", "phone_number")

    readonly_fields = ("joined_at", "license_image")

admin.site.register(User, UserAdmin)
