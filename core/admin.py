from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from core.models import ApiKey, AuditLog
import secrets


# Unregister the default User admin
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'role')
    list_filter = ('is_staff', 'role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "masked_key", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("key", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    actions = ["regenerate_keys"]

    @admin.action(description="Regenerate selected API keys")
    def regenerate_keys(self, request, queryset):
        count = 0
        for key_obj in queryset:
            old_prefix = (key_obj.key or "")[:6]
            key_obj.key = secrets.token_urlsafe(48)
            key_obj.save(update_fields=["key"])
            count += 1

            # Safe audit write — minimal inline logic; log full event in `action`
            try:
                AuditLog.objects.create(
                    user=(
                        request.user
                        if getattr(request, "user", None)
                        and request.user.is_authenticated
                        else None
                    ),
                    ip_address=request.META.get("REMOTE_ADDR", "")[:45] or None,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:200] or None,
                    endpoint="/admin/core/apikey/",
                    method="ADMIN",  # <= 10 chars — fits the DB column
                    action="API_KEY_REGENERATED",
                    payload={
                        "target": key_obj.name,
                        "old_key_prefix": old_prefix,
                        "new_key_prefix": key_obj.key[:6],
                    },
                    result_status="200",
                    created_at=timezone.now(),
                )
            except Exception as exc:
                # Don’t block the admin if audit fails
                self.message_user(
                    request,
                    f"Warning: audit log failed for {key_obj.name}: {exc}",
                    level="warning",
                )

        self.message_user(request, f"{count} API key(s) regenerated successfully.")

    def masked_key(self, obj):
        if obj.key:
            return f"{obj.key[:6]}...{obj.key[-4:]}"
        return "(none)"

    masked_key.short_description = "Key (masked)"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("key",)
        return self.readonly_fields
