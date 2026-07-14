from django.db import models

from tenancy.context import get_current_tenant_id


class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    def get_queryset(self):
        queryset = TenantQuerySet(self.model, using=self._db)
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return queryset.none()
        return queryset.filter(tenant_id=tenant_id)

    def for_tenant(self, tenant):
        return TenantQuerySet(self.model, using=self._db).for_tenant(tenant)
