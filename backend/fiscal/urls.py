from django.urls import path

from fiscal.views import FiscalConfigView, FiscalStatusView, RequestFiscalView
from fiscal.webhook import fiscal_webhook

app_name = 'fiscal'

urlpatterns = [
    path(
        'sales/<uuid:sale_id>/fiscal-status/',
        FiscalStatusView.as_view(),
        name='fiscal-status',
    ),
    path(
        'sales/<uuid:sale_id>/request-fiscal/',
        RequestFiscalView.as_view(),
        name='request-fiscal',
    ),
    path('fiscal/config/', FiscalConfigView.as_view(), name='fiscal-config'),
    path('fiscal/webhook/', fiscal_webhook, name='fiscal-webhook'),
]
