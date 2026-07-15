import pytest
from django.core.exceptions import ValidationError

from catalog.models import Category, Product, Unit
from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Tenant


@pytest.mark.django_db
def test_product_sku_is_normalized_and_unique_per_tenant():
    tenant = Tenant.objects.create(name='Loja', slug='loja-catalog')
    unit = Unit.all_objects.create(
        tenant=tenant, symbol='kg', name='Quilograma', precision=3,
    )
    first = Product.all_objects.create(
        tenant=tenant, sku=' racao-01 ', name='Ração', base_unit=unit,
    )
    assert first.sku == 'RACAO-01'
    with pytest.raises(Exception):
        Product.all_objects.create(
            tenant=tenant, sku='racao-01', name='Outra', base_unit=unit,
        )


@pytest.mark.django_db
def test_unit_symbol_is_unique_per_tenant():
    tenant = Tenant.objects.create(name='Unidades', slug='units-catalog')
    Unit.all_objects.create(tenant=tenant, symbol='KG', name='Quilo', precision=3)
    with pytest.raises(Exception):
        Unit.all_objects.create(tenant=tenant, symbol=' kg ', name='Quilo2', precision=3)


@pytest.mark.django_db
def test_unit_precision_validation_rejects_above_6():
    tenant = Tenant.objects.create(name='Prec', slug='prec-catalog')
    unit = Unit(tenant=tenant, symbol='X', name='X', precision=7)
    with pytest.raises(ValidationError):
        unit.full_clean()


@pytest.mark.django_db
def test_category_rejects_parent_cycle():
    tenant = Tenant.objects.create(name='Ciclo', slug='ciclo-catalog')
    parent = Category.all_objects.create(tenant=tenant, name='Pai')
    child = Category.all_objects.create(tenant=tenant, name='Filho', parent=parent)
    parent.parent = child
    with pytest.raises(ValidationError):
        parent.full_clean()


@pytest.mark.django_db
def test_product_requires_unit_of_same_tenant():
    tenant_a = Tenant.objects.create(name='A', slug='tenant-a-cat')
    tenant_b = Tenant.objects.create(name='B', slug='tenant-b-cat')
    unit_b = Unit.all_objects.create(
        tenant=tenant_b, symbol='kg', name='Kg', precision=3,
    )
    product = Product.all_objects.create(
        tenant=tenant_a, sku='P-1', name='P1', base_unit=unit_b,
    )
    with pytest.raises(ValidationError):
        product.full_clean()


@pytest.mark.django_db
def test_product_inactivation_preserves_record():
    tenant = Tenant.objects.create(name='Inat', slug='inat-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='un', name='Un', precision=0)
    product = Product.all_objects.create(
        tenant=tenant, sku='P-INAT', name='Produto', base_unit=unit,
    )
    product.is_active = False
    product.save()
    assert Product.all_objects.filter(pk=product.pk).exists()


@pytest.mark.django_db
def test_tenant_manager_filters_by_context():
    tenant = Tenant.objects.create(name='Ctx', slug='ctx-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='cx', name='Caixa', precision=0)
    token = set_current_tenant_id(tenant.id)
    try:
        assert Unit.objects.filter(pk=unit.pk).exists()
    finally:
        reset_current_tenant_id(token)


@pytest.mark.django_db
def test_tenant_manager_returns_none_without_context():
    tenant = Tenant.objects.create(name='NoCtx', slug='noctx-catalog')
    Unit.all_objects.create(tenant=tenant, symbol='un', name='Un', precision=0)
    assert Unit.objects.count() == 0