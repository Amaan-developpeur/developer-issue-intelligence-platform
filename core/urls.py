from django.urls import path
from .views import RegisterView, CustomLoginView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import GitHubWebhookView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("webhooks/github/", GitHubWebhookView.as_view(), name="github-webhook"),
]
