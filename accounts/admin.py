from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LicenseVerification
from django.utils.html import format_html

class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "phone_number", "role",
        "verification_status", "is_phone_verified",
        "is_staff", "is_active"
    )
    ordering = ("-joined_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("기본 정보", {
            "fields": (
                "phone_number", "role",
                "verification_status", "is_phone_verified",
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

    list_filter = ("role", "verification_status", "is_phone_verified", "is_staff")
    search_fields = ("username", "phone_number")
    readonly_fields = ("joined_at",)


@admin.register(LicenseVerification)
class LicenseVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "submitted_at", "document_preview")
    readonly_fields = ("submitted_at", "document_preview")

    def document_preview(self, obj):
        if obj.document and obj.document.url:
            return format_html(
                '<img src="{}" style="max-height: 300px; border: 1px solid #ccc;" />',
                obj.document.url
            )
        return "이미지 없음"


admin.site.register(User, UserAdmin)
