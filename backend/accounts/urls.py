from django.urls import path

from accounts.views.onboarding import EmailConfirmationView, RegistrationView

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegistrationView.as_view(), name='register'),
    path('auth/email/confirm/', EmailConfirmationView.as_view(), name='email-confirm'),
]
