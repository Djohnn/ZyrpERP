from django.urls import path

from fiscal.views import FiscalStatusView
from fiscal.webhook import fiscal_webhook

app_name = 'fiscal'

urlpatterns = [
    path(
        'sales/<uuid:sale_id>/fiscal-status/',
        FiscalStatusView.as_view(),
        name='fiscal-status',
    ),
    path('fiscal/webhook/', fiscal_webhook, name='fiscal-webhook'),
]
