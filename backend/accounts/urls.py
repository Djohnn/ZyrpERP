from django.urls import path

from accounts.views.onboarding import EmailConfirmationView, RegistrationView
from accounts.views.password import PasswordForgotView, PasswordResetView
from accounts.views.session import LoginView, LogoutView, MeView

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegistrationView.as_view(), name='register'),
    path('auth/email/confirm/', EmailConfirmationView.as_view(), name='email-confirm'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/password/forgot/', PasswordForgotView.as_view(), name='password-forgot'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='password-reset'),
]
