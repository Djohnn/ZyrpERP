from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from tenancy.managers import TenantManager
from tenancy.models import TenantScopedModel, TimeStampedModel


class VersionedInventoryModel(TimeStampedModel, TenantScopedModel):
    version = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True


class StockLocation(VersionedInventoryModel):
    LOCATION_TYPES = [
        ('warehouse', 'Armazem'),
        ('store', 'Loja'),
        ('counter', 'Balcao'),
        ('general', 'Geral'),
    ]

    branch = models.ForeignKey(
        'tenancy.Branch',
        on_delete=models.CASCADE,
        related_name='stock_locations',
    )
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        default='general',
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
        if self.branch_id and self.tenant_id and self.branch.tenant_id != self.tenant_id:
            raise ValidationError({'branch': 'Branch must belong to the same tenant.'})


class StockLot(VersionedInventoryModel):
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='stock_lots',
    )
    lot_number = models.CharField(max_length=64)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['product', 'lot_number']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'product', 'lot_number'],
                name='uniq_stocklot_tenant_product_number',
            ),
        ]

    def __str__(self):
        return f'{self.lot_number} ({self.product.sku})'

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.now().date())

    def clean(self):
        super().clean()
        if (
            self.manufacture_date
            and self.expiry_date
            and self.manufacture_date >= self.expiry_date
        ):
            raise ValidationError(
                {'expiry_date': 'Expiry date must be after manufacture date.'}
            )
        if self.product_id and self.tenant_id and self.product.tenant_id != self.tenant_id:
            raise ValidationError({'product': 'Product must belong to the same tenant.'})


class StockOperation(VersionedInventoryModel):
    TYPE_CHOICES = [
        ('receipt', 'Entrada'),
        ('issue', 'Saida'),
        ('adjustment', 'Ajuste'),
        ('transfer', 'Transferencia'),
        ('reversal', 'Reversao'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('reversed', 'Revertida'),
    ]

    operation_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    branch = models.ForeignKey(
        'tenancy.Branch',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='stock_operations',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_operations',
    )
    idempotency_key = models.CharField(max_length=100, blank=True, default='')
    payload_hash = models.CharField(max_length=64, blank=True, default='')
    reference = models.CharField(max_length=100, blank=True, default='')
    reason = models.TextField(blank=True, default='')

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'idempotency_key'],
                name='uniq_stockoperation_tenant_idempotency',
                condition=models.Q(idempotency_key__gt=''),
            ),
        ]

    def clean(self):
        super().clean()
        if self.branch_id and self.tenant_id and self.branch.tenant_id != self.tenant_id:
            raise ValidationError({'branch': 'Branch must belong to the same tenant.'})
        if self.idempotency_key:
            exists = StockOperation.all_objects.filter(
                tenant_id=self.tenant_id,
                idempotency_key=self.idempotency_key,
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError({'idempotency_key': 'Idempotency key already used.'})


class StockMovement(VersionedInventoryModel):
    DIRECTION_CHOICES = [
        ('in', 'Entrada'),
        ('out', 'Saida'),
    ]

    operation = models.ForeignKey(
        'inventory.StockOperation',
        on_delete=models.PROTECT,
        related_name='movements',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='stock_movements',
    )
    location = models.ForeignKey(
        'inventory.StockLocation',
        on_delete=models.PROTECT,
        related_name='movements',
    )
    lot = models.ForeignKey(
        'inventory.StockLot',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='stock_movements',
    )
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    quantity = models.DecimalField(max_digits=18, decimal_places=6)
    unit = models.ForeignKey(
        'catalog.Unit',
        on_delete=models.PROTECT,
        related_name='stock_movements',
    )
    factor = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['created_at']

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be positive.'})
        if self.factor <= 0:
            raise ValidationError({'factor': 'Factor must be positive.'})
        if self.product_id and self.tenant_id and self.product.tenant_id != self.tenant_id:
            raise ValidationError({'product': 'Product must belong to the same tenant.'})
        if self.location_id and self.tenant_id and self.location.tenant_id != self.tenant_id:
            raise ValidationError({'location': 'Location must belong to the same tenant.'})
        if self.unit_id and self.tenant_id and self.unit.tenant_id != self.tenant_id:
            raise ValidationError({'unit': 'Unit must belong to the same tenant.'})
        if self.lot_id and self.tenant_id:
            if self.lot.tenant_id != self.tenant_id:
                raise ValidationError({'lot': 'Lot must belong to the same tenant.'})
            if self.lot.product_id != self.product_id:
                raise ValidationError({'lot': 'Lot must belong to the same product.'})

    def save(self, *args, **kwargs):
        if not self._state.adding:
            current = StockMovement.all_objects.select_related('operation').get(pk=self.pk)
            if current.operation.status == 'confirmed':
                raise ValidationError('Confirmed stock movements are immutable.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.operation.status == 'confirmed':
            raise ValidationError('Confirmed stock movements cannot be deleted.')
        return super().delete(*args, **kwargs)


class StockBalance(VersionedInventoryModel):
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='stock_balances',
    )
    location = models.ForeignKey(
        'inventory.StockLocation',
        on_delete=models.PROTECT,
        related_name='stock_balances',
    )
    lot = models.ForeignKey(
        'inventory.StockLot',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='stock_balances',
    )
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    reserved = models.DecimalField(max_digits=18, decimal_places=6, default=0)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['product', 'location', 'lot']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'product', 'location', 'lot'],
                name='uniq_stockbalance_tenant_product_location_lot',
            ),
        ]

    @property
    def available(self):
        return self.quantity - self.reserved

    def __str__(self):
        lot_str = f' lot:{self.lot.lot_number}' if self.lot else ''
        return f'{self.product.sku} @ {self.location.code}{lot_str} = {self.quantity}'

    def clean(self):
        super().clean()
        if self.quantity < 0:
            raise ValidationError({'quantity': 'Quantity cannot be negative.'})
        if self.reserved < 0:
            raise ValidationError({'reserved': 'Reserved cannot be negative.'})
        if self.reserved > self.quantity:
            raise ValidationError({'reserved': 'Reserved cannot exceed quantity.'})
        if self.product_id and self.tenant_id and self.product.tenant_id != self.tenant_id:
            raise ValidationError({'product': 'Product must belong to the same tenant.'})
        if self.location_id and self.tenant_id and self.location.tenant_id != self.tenant_id:
            raise ValidationError({'location': 'Location must belong to the same tenant.'})
        if self.lot_id and self.tenant_id:
            if self.lot.tenant_id != self.tenant_id:
                raise ValidationError({'lot': 'Lot must belong to the same tenant.'})
            if self.lot.product_id != self.product_id:
                raise ValidationError({'lot': 'Lot must belong to the same product.'})


def _location_has_history(location):
    return (
        StockMovement.all_objects.filter(location=location).exists()
        or StockBalance.all_objects.filter(location=location)
        .exclude(quantity=0, reserved=0)
        .exists()
    )


def _protected_stock_location_delete(self, *args, **kwargs):
    if _location_has_history(self):
        raise ValidationError('Stock location with history cannot be deleted.')
    return super(StockLocation, self).delete(*args, **kwargs)


StockLocation.delete = _protected_stock_location_delete


class StockOperationReversal(VersionedInventoryModel):
    original_operation = models.ForeignKey(
        'inventory.StockOperation',
        on_delete=models.PROTECT,
        related_name='reversals',
    )
    reversal_operation = models.OneToOneField(
        'inventory.StockOperation',
        on_delete=models.PROTECT,
        related_name='reversal_of',
    )
    reason = models.TextField()

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'original_operation'],
                name='uniq_stockoperationreversal_original',
            ),
        ]

    def clean(self):
        super().clean()
        if (
            self.original_operation_id
            and self.tenant_id
            and self.original_operation.tenant_id != self.tenant_id
        ):
            raise ValidationError(
                {'original_operation': 'Original operation must belong to the same tenant.'}
            )
        if (
            self.reversal_operation_id
            and self.tenant_id
            and self.reversal_operation.tenant_id != self.tenant_id
        ):
            raise ValidationError(
                {'reversal_operation': 'Reversal operation must belong to the same tenant.'}
            )
