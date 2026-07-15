from decimal import Decimal

import pytest

from catalog.models import Product, ProductCode, ProductUnit, Unit
from tenancy.models import Tenant


@pytest.mark.django_db
def test_product_code_active_unique_per_tenant():
    tenant = Tenant.objects.create(name='Cod', slug='cod-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='un', name='Un', precision=0)
    product = Product.all_objects.create(
        tenant=tenant, sku='P-1', name='P1', base_unit=unit,
    )
    ProductCode.all_objects.create(
        tenant=tenant, product=product, code_type='internal', value='COD-1',
        is_active=True,
    )
    with pytest.raises(Exception):
        ProductCode.all_objects.create(
            tenant=tenant, product=product, code_type='internal', value='COD-1',
            is_active=True,
        )


@pytest.mark.django_db
def test_product_code_value_is_normalized():
    tenant = Tenant.objects.create(name='Norm', slug='norm-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='un', name='Un', precision=0)
    product = Product.all_objects.create(
        tenant=tenant, sku='P-N', name='PN', base_unit=unit,
    )
    code = ProductCode.all_objects.create(
        tenant=tenant, product=product, code_type='internal',
        value=' cod-001 ', is_active=True,
    )
    assert code.value == 'COD-001'


@pytest.mark.django_db
def test_product_code_tenant_must_match_product_tenant():
    tenant_a = Tenant.objects.create(name='A', slug='code-a')
    tenant_b = Tenant.objects.create(name='B', slug='code-b')
    unit_b = Unit.all_objects.create(tenant=tenant_b, symbol='un', name='Un', precision=0)
    product_b = Product.all_objects.create(
        tenant=tenant_b, sku='P-B', name='PB', base_unit=unit_b,
    )
    code = ProductCode(
        tenant=tenant_a, product=product_b, code_type='internal',
        value='X', is_active=True,
    )
    with pytest.raises(Exception):
        code.full_clean()


@pytest.mark.django_db
def test_one_principal_code_per_product_and_type():
    tenant = Tenant.objects.create(name='Princ', slug='princ-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='un', name='Un', precision=0)
    product = Product.all_objects.create(
        tenant=tenant, sku='P-PR', name='PPr', base_unit=unit,
    )
    ProductCode.all_objects.create(
        tenant=tenant, product=product, code_type='ean',
        value='7894900011517', is_active=True, is_principal=True,
    )
    with pytest.raises(Exception):
        ProductCode.all_objects.create(
            tenant=tenant, product=product, code_type='ean',
            value='7891000315507', is_active=True, is_principal=True,
        )


@pytest.mark.django_db
def test_product_unit_factor_must_be_positive():
    tenant = Tenant.objects.create(name='PU', slug='pu-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='kg', name='Kg', precision=3)
    unit_sc = Unit.all_objects.create(tenant=tenant, symbol='sc', name='Saco', precision=0)
    product = Product.all_objects.create(
        tenant=tenant, sku='P-PU', name='PPU', base_unit=unit,
    )
    pu = ProductUnit(
        tenant=tenant, product=product, unit=unit_sc, factor=Decimal('0'),
    )
    with pytest.raises(Exception):
        pu.full_clean()


@pytest.mark.django_db
def test_product_unit_tenant_must_match():
    tenant_a = Tenant.objects.create(name='A', slug='pu-a')
    tenant_b = Tenant.objects.create(name='B', slug='pu-b')
    unit_a = Unit.all_objects.create(tenant=tenant_a, symbol='kg', name='Kg', precision=3)
    unit_b = Unit.all_objects.create(tenant=tenant_b, symbol='sc', name='Sc', precision=0)
    product_a = Product.all_objects.create(
        tenant=tenant_a, sku='PA', name='PA', base_unit=unit_a,
    )
    pu = ProductUnit(
        tenant=tenant_a, product=product_a, unit=unit_b, factor=Decimal('20'),
    )
    with pytest.raises(Exception):
        pu.full_clean()