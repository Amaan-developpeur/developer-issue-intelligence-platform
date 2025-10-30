from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta
from core.models import UserSession
from core.serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view


# Create your views here.
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class CustomLoginView(TokenObtainPairView):
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
                user_agent=request.META.get('HTTP_USER_AGENT'),
                expires_at=expires_at
            )
        return response
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                raise ValidationError({"error": "Refresh token required"})

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Deactivate session record
            from core.models import UserSession
            session = UserSession.objects.filter(
                user=request.user,
                refresh_token=refresh_token,
                is_active=True
            ).first()
            if session:
                session.is_active = False
                session.save()

            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

from core.permissions import IsAdminOrReadOnly
from rest_framework.decorators import api_view, permission_classes


        

@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def task_dashboard(request):
    results = TaskResult.objects.order_by("-date_done")[:10]
    return Response([
        {
            "task": r.task_name,
            "status": r.status,
            "timestamp": r.date_done,
            "result": r.result,
        }
        for r in results
    ])