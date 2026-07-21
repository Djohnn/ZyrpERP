from rest_framework.permissions import BasePermission

from tenancy.capabilities import role_allows
from tenancy.models import TenantMembership


class PurchasingCapabilityPermission(BasePermission):
    read_capability = 'purchasing.view'
    write_capability = 'purchasing.manage'

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return False
        membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True,
        ).first()
        if membership is None:
            return False
        if getattr(view, 'action', '') in {'list', 'retrieve'}:
            return role_allows(membership.role, self.read_capability)
        return role_allows(membership.role, self.write_capability)
