from django.urls import path

from accounts.views.onboarding import EmailConfirmationView, RegistrationView
from accounts.views.session import LoginView, LogoutView, MeView

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegistrationView.as_view(), name='register'),
    path('auth/email/confirm/', EmailConfirmationView.as_view(), name='email-confirm'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
]
