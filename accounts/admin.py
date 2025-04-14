from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LicenseVerification


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
    list_display = ("user", "status", "submitted_at", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__phone_number")
    readonly_fields = ("submitted_at",)

    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="✅ 선택한 유저 인증 승인")
    def approve_selected(self, request, queryset):
        for license in queryset:
            license.approve()
        self.message_user(request, f"{queryset.count()}명의 유저 인증이 승인되었습니다.")

    @admin.action(description="❌ 선택한 유저 인증 반려")
    def reject_selected(self, request, queryset):
        for license in queryset:
            license.reject()
        self.message_user(request, f"{queryset.count()}명의 유저 인증이 반려되었습니다.")


admin.site.register(User, UserAdmin)
