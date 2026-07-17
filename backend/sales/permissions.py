from rest_framework.permissions import BasePermission

from tenancy.capabilities import role_allows
from tenancy.models import TenantMembership


class SalesCapabilityPermission(BasePermission):
    read_capability = 'sales.view'
    write_capability = 'sales.sell'
    cash_capability = 'sales.cash.manage'

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
        action = getattr(view, 'action', '')
        if action in {'list', 'retrieve', 'current'}:
            return role_allows(membership.role, self.read_capability)
        if action in {'open', 'close'}:
            return role_allows(membership.role, self.cash_capability)
        return role_allows(membership.role, self.write_capability)
