from django.core.exceptions import ValidationError
from django.db import models

from tenancy.managers import TenantManager
from tenancy.models import TenantScopedModel, TimeStampedModel


class StockLocation(TimeStampedModel, TenantScopedModel):
    LOCATION_TYPES = [
        ('warehouse', 'Armazém'),
        ('store', 'Loja'),
        ('counter', 'Balcão'),
        ('general', 'Geral'),
    ]

    branch = models.ForeignKey(
        'tenancy.Branch', on_delete=models.CASCADE,
        related_name='stock_locations',
    )
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    location_type = models.CharField(
        max_length=20, choices=LOCATION_TYPES, default='general',
    )
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['branch', 'code']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'branch', 'code'],
                name='uniq_stocklocation_branch_code',
            ),
            models.UniqueConstraint(
                fields=['tenant', 'branch'],
                condition=models.Q(is_primary=True) & models.Q(is_active=True),
                name='uniq_primary_location_per_branch',
            ),
        ]

    def __str__(self):
        return f'{self.name} [{self.branch.name}]'

    def save(self, *args, **kwargs):
        if self.is_primary and self.is_active:
            StockLocation.all_objects.filter(
                tenant_id=self.tenant_id,
                branch_id=self.branch_id,
                is_primary=True,
                is_active=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.branch_id and self.tenant_id:
            if self.branch.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'branch': 'Branch must belong to the same tenant.'}
                )