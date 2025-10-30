from django.db import models
from django.contrib.auth.models import User
import secrets 


# --- Extend the built-in User model first ---
User.add_to_class(
    'role',
    models.CharField(
        max_length=32,
        null=True,
        blank=True,
        choices=[
            ('admin', 'Admin'),
            ('developer', 'Developer'),
            ('analyst', 'Analyst'),
            ('viewer', 'Viewer'),
        ],
    ),
)

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    

    def __str__(self):
        return f"{self.user.username} - {self.ip_address or 'unknown'}"
    

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    action = models.CharField(max_length=50, null=True, blank=True)
    payload = models.JSONField(null=True, blank=True)
    result_status = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.endpoint} [{self.method}]"

    




def generate_api_key():
    return secrets.token_urlsafe(48)

class ApiKey(models.Model):
    name = models.CharField(max_length=64)
    key = models.CharField(
        max_length=128,
        unique=True,
        default=generate_api_key,  
    )
    scopes = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'revoked'})"
    
    def regenerate_key(self):
        self.key = secrets.token_urlsafe(48)
        self.save(update_fields=["key"])
        return self.key



