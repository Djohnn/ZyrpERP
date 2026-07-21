from rest_framework.permissions import BasePermission

from tenancy.capabilities import role_allows
from tenancy.models import TenantMembership


class FinancialReportingPermission(BasePermission):
    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return False
        membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True,
        ).first()
        return bool(membership and role_allows(membership.role, 'financial.view'))
