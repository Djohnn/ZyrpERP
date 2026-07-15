from django.core.exceptions import ValidationError
from django.db import models

from tenancy.managers import TenantManager
from tenancy.models import TenantScopedModel, TimeStampedModel


class Unit(TimeStampedModel, TenantScopedModel):
    symbol = models.CharField(max_length=12)
    name = models.CharField(max_length=80)
    precision = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['symbol']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'symbol'], name='uniq_unit_tenant_symbol',
            ),
            models.CheckConstraint(
                condition=models.Q(precision__lte=6),
                name='unit_precision_max_6',
            ),
        ]

    def __str__(self):
        return f'{self.symbol} [{self.tenant.name}]'

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.strip().upper()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.precision > 6:
            raise ValidationError({'precision': 'Precision must not exceed 6.'})


class Category(TimeStampedModel, TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, blank=True, default='')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.PROTECT,
    )
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                condition=models.Q(~models.Q(code='')),
                name='uniq_category_tenant_code',
            ),
        ]

    def __str__(self):
        return f'{self.name} [{self.tenant.name}]'

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.parent_id == self.pk:
                raise ValidationError({'parent': 'Category cannot be its own parent.'})
            current = self.parent
            visited = {self.pk} if self.pk else set()
            while current is not None:
                if current.pk in visited:
                    raise ValidationError({'parent': 'Category hierarchy contains a cycle.'})
                visited.add(current.pk)
                if current.tenant_id != self.tenant_id:
                    raise ValidationError(
                        {'parent': 'Parent category must belong to the same tenant.'}
                    )
                current = current.parent


class Product(TimeStampedModel, TenantScopedModel):
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.PROTECT,
    )
    base_unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    requires_lot = models.BooleanField(default=False)
    requires_expiry = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['sku']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'sku'], name='uniq_product_tenant_sku',
            ),
        ]

    def __str__(self):
        return f'{self.sku} [{self.tenant.name}]'

    def save(self, *args, **kwargs):
        self.sku = self.sku.strip().upper()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.base_unit_id and self.tenant_id:
            if self.base_unit.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'base_unit': 'Base unit must belong to the same tenant.'}
                )
        if self.category_id and self.tenant_id:
            if self.category.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'category': 'Category must belong to the same tenant.'}
                )


class ProductUnit(TimeStampedModel, TenantScopedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='commercial_units',
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    factor = models.DecimalField(max_digits=18, decimal_places=6)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['product', 'unit']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'product', 'unit'],
                name='uniq_productunit_tenant_product_unit',
            ),
            models.CheckConstraint(
                condition=models.Q(factor__gt=0),
                name='productunit_factor_positive',
            ),
        ]

    def __str__(self):
        return f'{self.product.sku} → {self.unit.symbol} ×{self.factor}'

    def clean(self):
        super().clean()
        if self.factor <= 0:
            raise ValidationError({'factor': 'Conversion factor must be positive.'})
        if self.product_id and self.tenant_id:
            if self.product.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'product': 'Product must belong to the same tenant.'}
                )
        if self.unit_id and self.tenant_id:
            if self.unit.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'unit': 'Unit must belong to the same tenant.'}
                )


CODE_TYPE_CHOICES = [
    ('internal', 'Internal'),
    ('ean', 'EAN'),
    ('gtin', 'GTIN'),
    ('supplier', 'Supplier'),
]


class ProductCode(TimeStampedModel, TenantScopedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='codes',
    )
    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES)
    value = models.CharField(max_length=64)
    is_principal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['product', 'code_type', 'value']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code_type', 'value'],
                condition=models.Q(is_active=True),
                name='uniq_productcode_tenant_type_value_active',
            ),
            models.UniqueConstraint(
                fields=['tenant', 'product', 'code_type'],
                condition=models.Q(is_principal=True),
                name='uniq_productcode_principal_per_type',
            ),
        ]

    def __str__(self):
        return f'{self.value} ({self.code_type}) [{self.tenant.name}]'

    def save(self, *args, **kwargs):
        self.value = self.value.strip().upper()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.product_id and self.tenant_id:
            if self.product.tenant_id != self.tenant_id:
                raise ValidationError(
                    {'product': 'Product must belong to the same tenant.'}
                )
        if self.code_type in ('ean', 'gtin'):
            from catalog.services.codes import validate_gtin

            if not validate_gtin(self.value):
                raise ValidationError(
                    {'value': f'Invalid {self.code_type.upper()} check digit.'}
                )