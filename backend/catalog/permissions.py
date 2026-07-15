from rest_framework.permissions import BasePermission

from tenancy.capabilities import role_allows
from tenancy.models import TenantMembership

_READ_ACTIONS = {'list', 'retrieve'}


class CatalogCapabilityPermission(BasePermission):
    manage_capability = 'catalog.manage'
    view_capability = 'catalog.view'

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return False
        membership = TenantMembership.objects.filter(
            user=request.user, tenant=tenant, is_active=True,
        ).first()
        if membership is None:
            return False
        action = getattr(view, 'action', '')
        if action in _READ_ACTIONS:
            return role_allows(membership.role, self.view_capability)
        return role_allows(membership.role, self.manage_capability)


class PricingCapabilityPermission(CatalogCapabilityPermission):
    manage_capability = 'pricing.manage'
    view_capability = 'pricing.view'