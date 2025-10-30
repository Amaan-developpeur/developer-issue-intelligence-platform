from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django_celery_results.models import TaskResult

from core.models import UserSession
from core.serializers import CustomTokenObtainPairSerializer
from core.permissions import HasScope
from core.throttles import DashboardThrottle


# -------------------------------------------------------------
# USER REGISTRATION
# -------------------------------------------------------------
class RegisterSerializer(ModelSerializer):
    """Serializer for new user registration."""

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create user with encrypted password."""
        return User.objects.create_user(**validated_data)


class RegisterView(generics.CreateAPIView):
    """Register a new user."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# -------------------------------------------------------------
# LOGIN (JWT)
# -------------------------------------------------------------
class CustomLoginView(TokenObtainPairView):
    """JWT Login + persistent user session tracking."""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            refresh_token = response.data.get('refresh')
            expires_at = timezone.now() + timedelta(days=7)

            UserSession.objects.create(
                user=user,
                refresh_token=refresh_token,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=expires_at,
            )
        return response


# -------------------------------------------------------------
# LOGOUT (BLACKLIST REFRESH TOKEN)
# -------------------------------------------------------------
class LogoutView(APIView):
    """Logout user by blacklisting the refresh token and deactivating session."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            raise ValidationError({"error": "Refresh token required"})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            session = UserSession.objects.filter(
                user=request.user,
                refresh_token=refresh_token,
                is_active=True,
            ).first()

            if session:
                session.is_active = False
                session.save()

            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------
# TASK DASHBOARD (API KEY PROTECTED)
# -------------------------------------------------------------
@api_view(["GET"])
@permission_classes([HasScope("tasks:read")])
@throttle_classes([DashboardThrottle])
def task_dashboard(request):
    """Return the latest 10 Celery task results, rate-limited and API-key secured."""
    print("DEBUG: API key detected:", getattr(request, "api_key", None))

    results = TaskResult.objects.order_by("-date_done")[:10]
    data = [
        {
            "task": r.task_name,
            "status": r.status,
            "timestamp": r.date_done,
            "result": r.result,
        }
        for r in results
    ]

    return Response(data, status=status.HTTP_200_OK)


from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response

class GitHubWebhookView(APIView):
    permission_classes = [AllowAny]  # disable auth
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "webhook"       # custom throttle scope

    def post(self, request, *args, **kwargs):
        # handle webhook payload
        return Response({"status": "received"})
