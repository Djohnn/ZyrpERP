from django.http import Http404
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from fiscal.models import FiscalDocument
from fiscal.serializers import FiscalStatusSerializer
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
