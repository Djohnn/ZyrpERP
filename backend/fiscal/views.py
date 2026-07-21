from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fiscal.models import FiscalDocument
from fiscal.ocr import parse_nfe_xml
from fiscal.serializers import FiscalRequestSerializer, FiscalStatusSerializer
from fiscal.services import emit_nfce, reconcile_receipt_fiscal, resolve_emitter
from tenancy.permissions import HasActiveTenant, HasVerifiedMFA


class FiscalStatusView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, HasActiveTenant, HasVerifiedMFA]
    serializer_class = FiscalStatusSerializer

    def get_object(self):
        doc = FiscalDocument.all_objects.filter(
            sale_id=self.kwargs['sale_id'],
            tenant=self.request.tenant,
        ).order_by('-attempt_number').first()
        if doc is None:
            raise Http404('Fiscal document not found.')
        return doc


class RequestFiscalView(CreateAPIView):
    permission_classes = [IsAuthenticated, HasActiveTenant, HasVerifiedMFA]
    serializer_class = FiscalRequestSerializer

    def create(self, request, *args, **kwargs):
        from sales.models import Sale

        sale_id = self.kwargs.get('sale_id') or request.data.get('sale_id')
        try:
            sale = Sale.all_objects.select_related('branch', 'tenant').get(
                id=sale_id,
                tenant=request.tenant,
            )
        except Sale.DoesNotExist:
            return Response(
                {'detail': 'Venda não encontrada.'},
                status=404,
            )

        if sale.status != 'confirmed':
            return Response(
                {'detail': 'Apenas vendas confirmadas podem solicitar emissão fiscal.'},
                status=400,
            )

        doc = emit_nfce(sale, request.tenant)

        return Response(
            FiscalStatusSerializer(doc).data,
            status=201,
        )


class FiscalConfigView(APIView):
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get(self, request):
        from tenancy.models import Branch

        branch_id = request.query_params.get('branch')
        if not branch_id:
            return Response({'detail': 'branch query parameter is required.'}, status=400)
        try:
            branch = Branch.all_objects.get(id=branch_id, tenant=request.tenant)
        except Branch.DoesNotExist:
            return Response({'detail': 'Branch not found.'}, status=404)

        emitter = resolve_emitter(branch)
        return Response({
            'has_fiscal_config': emitter is not None,
            'emitter_id': str(emitter.id) if emitter else None,
        })


class OCRNFeView(APIView):
    permission_classes = [IsAuthenticated, HasActiveTenant, HasVerifiedMFA]

    def post(self, request):
        xml_content = request.data.get('xml_content', '')
        if not xml_content:
            return Response({'detail': 'xml_content is required.'}, status=400)
        try:
            result = parse_nfe_xml(xml_content)
        except Exception as exc:
            return Response(
                {'detail': f'Falha ao processar XML: {exc}'},
                status=400,
            )
        return Response(result)


class ReceiptFiscalValidateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveTenant, HasVerifiedMFA]

    def post(self, request, receipt_id):
        from purchasing.models import PurchaseReceipt

        try:
            receipt = PurchaseReceipt.all_objects.select_related(
                'purchase_order__supplier',
                'purchase_order__branch',
            ).get(id=receipt_id, tenant=request.tenant)
        except PurchaseReceipt.DoesNotExist:
            return Response({'detail': 'Recebimento não encontrado.'}, status=404)

        cfop = request.data.get('cfop', '')
        result = reconcile_receipt_fiscal(receipt, request.tenant, cfop=cfop or None)

        return Response({
            'receipt_id': str(receipt.id),
            'cfop': result['document'].cfop if result['document'] else (cfop or ''),
            'issues': result['issues'],
            'warnings': result['warnings'],
            'requires_attention': bool(result['issues']),
            'created': result['document'] is not None,
            'document_id': str(result['document'].id) if result['document'] else None,
        })
