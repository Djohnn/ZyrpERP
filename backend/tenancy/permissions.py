from rest_framework.permissions import BasePermission


class HasActiveTenant(BasePermission):
    message = 'A valid X-Tenant-ID header is required.'

    def has_permission(self, request, view):
        return getattr(request, 'tenant', None) is not None
