from django.db import models
from django.contrib.auth.models import User


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
