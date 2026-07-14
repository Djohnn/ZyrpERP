from django.http import JsonResponse


class TenantRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, 'tenant', None):
            return JsonResponse(
                {'detail': 'Tenant context is required.'},
                status=403,
            )
        return super().dispatch(request, *args, **kwargs)
