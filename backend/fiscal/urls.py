from django.urls import path

from fiscal.views import (
    FiscalConfigView,
    FiscalStatusView,
    OCRNFeView,
    ReceiptFiscalValidateView,
    RequestFiscalView,
)
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
    path('fiscal/ocr/', OCRNFeView.as_view(), name='fiscal-ocr'),
    path('fiscal/config/', FiscalConfigView.as_view(), name='fiscal-config'),
    path('fiscal/webhook/', fiscal_webhook, name='fiscal-webhook'),
    path(
        'receipts/<uuid:receipt_id>/validate-fiscal/',
        ReceiptFiscalValidateView.as_view(),
        name='receipt-validate-fiscal',
    ),
]
