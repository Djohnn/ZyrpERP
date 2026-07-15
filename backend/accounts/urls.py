from django.urls import path

from accounts.views.onboarding import EmailConfirmationView, RegistrationView
from accounts.views.mfa import (
    EmailMFASendView,
    MFAChallengeView,
    RecoveryRegenerateView,
    TOTPConfirmationView,
    TOTPEnrollmentView,
)
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
    path('auth/mfa/totp/enroll/', TOTPEnrollmentView.as_view(), name='totp-enroll'),
    path('auth/mfa/totp/confirm/', TOTPConfirmationView.as_view(), name='totp-confirm'),
    path('auth/mfa/email/send/', EmailMFASendView.as_view(), name='email-mfa-send'),
    path('auth/mfa/challenge/', MFAChallengeView.as_view(), name='mfa-challenge'),
    path('auth/mfa/recovery/regenerate/', RecoveryRegenerateView.as_view(), name='recovery-regenerate'),
]
