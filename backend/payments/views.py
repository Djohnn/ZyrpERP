from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import Sale
from tenancy.permissions import HasActiveTenant

from .models import (
    PaymentProviderConfig,
    PaymentReconciliationBatch,
    PaymentTransaction,
)
from .serializers import (
    PaymentIntentInputSerializer,
    PaymentIntentSerializer,
    PaymentReconciliationBatchSerializer,
    PaymentTransactionSerializer,
    PaymentWebhookEventSerializer,
    ReconciliationBatchInputSerializer,
)
from .services import (
    InvalidWebhookSignature,
    ReconciliationDivergence,
    confirm_reconciliation,
    create_payment_intent,
    import_reconciliation_batch,
    process_webhook,
)


def _problem(detail, code, status_code):
    return Response({
        'type': f'https://docs.zyrp.local/errors/{code}',
        'title': code.replace('_', ' ').title(),
        'status': status_code,
        'detail': str(detail),
        'code': code,
    }, status=status_code, content_type='application/problem+json')


class PaymentIntentCreateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def post(self, request):
        serializer = PaymentIntentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sale = Sale.all_objects.filter(tenant=request.tenant, id=data['sale']).first()
        config = PaymentProviderConfig.all_objects.filter(
            tenant=request.tenant, id=data['provider_config'], is_active=True,
        ).first()
        if sale is None or config is None:
            return _problem('Sale or provider config not found.', 'not_found', 404)
        intent = create_payment_intent(
            tenant=request.tenant, sale=sale, provider_config=config,
            idempotency_key=data['idempotency_key'], actor=request.user,
        )
        return Response(PaymentIntentSerializer(intent).data, status=status.HTTP_201_CREATED)


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return PaymentTransaction.all_objects.filter(tenant=self.request.tenant)


class PaymentReconciliationBatchViewSet(viewsets.GenericViewSet):
    serializer_class = PaymentReconciliationBatchSerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return PaymentReconciliationBatch.all_objects.filter(tenant=self.request.tenant)

    def create(self, request):
        serializer = ReconciliationBatchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = import_reconciliation_batch(
            tenant=request.tenant, **serializer.validated_data,
        )
        return Response(self.get_serializer(batch).data, status=201)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            batch = confirm_reconciliation(batch=self.get_object(), actor=request.user)
        except ReconciliationDivergence as exc:
            return _problem(exc, 'reconciliation_divergence', 409)
        return Response(self.get_serializer(batch).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasActiveTenant])
def payment_webhook(request, provider):
    try:
        event = process_webhook(
            tenant=request.tenant, provider=provider, payload=request.body,
            signature=request.headers.get('X-Payment-Signature', ''),
        )
    except InvalidWebhookSignature as exc:
        return _problem(exc, 'invalid_webhook_signature', 400)
    except PaymentProviderConfig.DoesNotExist:
        return _problem('Provider not configured.', 'provider_not_found', 404)
    return Response(PaymentWebhookEventSerializer(event).data)
