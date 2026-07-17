from rest_framework.permissions import BasePermission

from tenancy.capabilities import role_allows
from tenancy.models import TenantMembership


class RequireCapability(BasePermission):
    def __init__(self, capability):
        self.capability = capability

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return False
        membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True,
        ).first()
        return bool(membership and role_allows(membership.role, self.capability))


class InventoryCapabilityPermission(BasePermission):
    read_capability = 'inventory.view'
    write_capability = 'inventory.adjust'

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
        if getattr(view, 'action', '') in {'list', 'retrieve', 'summary'}:
            return role_allows(membership.role, self.read_capability)
        return role_allows(membership.role, self.write_capability)


class InventoryLocationsPermission(InventoryCapabilityPermission):
    write_capability = 'inventory.locations.manage'
