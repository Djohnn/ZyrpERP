from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from audit.services import create_audit_record
from tenancy.models import Company
from tenancy.permissions import HasActiveTenant
from tenancy.serializers import CompanySerializer


class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return Company.objects.filter(tenant=self.request.tenant).order_by('name')

    def perform_create(self, serializer):
        company = serializer.save(tenant=self.request.tenant)
        create_audit_record(
            actor=self.request.user,
            action='company.created',
            resource_type='Company',
            resource_id=company.id,
            tenant_id=self.request.tenant.id,
            correlation_id=getattr(self.request, 'correlation_id', ''),
            detail={'name': company.name},
        )


class CompanyDetailView(generics.RetrieveAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return Company.objects.filter(tenant=self.request.tenant)
