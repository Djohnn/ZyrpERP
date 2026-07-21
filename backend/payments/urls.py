from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentIntentCreateView,
    PaymentReconciliationBatchViewSet,
    PaymentTransactionViewSet,
    payment_webhook,
)

router = DefaultRouter()
router.register('payments/transactions', PaymentTransactionViewSet, basename='payment-transaction')
router.register(
    'payments/reconciliation-batches', PaymentReconciliationBatchViewSet,
    basename='payment-reconciliation-batch',
)

urlpatterns = [
    path('payments/intents/', PaymentIntentCreateView.as_view(), name='payment-intent-create'),
    path('payments/webhooks/<str:provider>/', payment_webhook, name='payment-webhook'),
] + router.urls
