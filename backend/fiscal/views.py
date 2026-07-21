from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fiscal.models import FiscalDocument
from fiscal.serializers import FiscalRequestSerializer, FiscalStatusSerializer
from fiscal.services import emit_nfce, resolve_emitter
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
