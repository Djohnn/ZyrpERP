from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import connection, transaction

from catalog.models import Product, Unit
from inventory.models import StockBalance, StockLocation, StockLot, StockMovement
from inventory.services import (
    DuplicateIdempotencyKey,
    ExpiredLotError,
    InvalidLotError,
    create_adjustment,
    create_issue,
    create_receipt,
    create_transfer,
    get_stock_balance,
    reconcile_stock_balances,
    reverse_operation,
)
from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Branch, Company, Tenant


def run_in_tenant(tenant, callback):
    token = set_current_tenant_id(tenant.id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(tenant.id)],
            )
        return callback()
    finally:
        reset_current_tenant_id(token)


@pytest.fixture
def stock_context():
    tenant = Tenant.objects.create(name='Sprint 3 Tenant', slug='sprint3-tenant')

    def _create():
        unit = Unit.all_objects.create(
            tenant=tenant,
            symbol='UN',
            name='Unidade',
            precision=0,
        )
        product = Product.all_objects.create(
            tenant=tenant,
            sku='S3-PROD',
            name='Produto Sprint 3',
            base_unit=unit,
            requires_lot=True,
            requires_expiry=True,
        )
        company = Company.all_objects.create(tenant=tenant, name='Empresa S3')
        branch = Branch.all_objects.create(
            tenant=tenant,
            company=company,
            name='Filial S3',
        )
        source = StockLocation.all_objects.create(
            tenant=tenant,
            branch=branch,
            code='SRC',
            name='Origem',
            is_primary=True,
        )
        target = StockLocation.all_objects.create(
            tenant=tenant,
            branch=branch,
            code='DST',
            name='Destino',
        )
        valid_lot = StockLot.all_objects.create(
            tenant=tenant,
            product=product,
            lot_number='VALID',
            expiry_date=date.today() + timedelta(days=30),
        )
        expired_lot = StockLot.all_objects.create(
            tenant=tenant,
            product=product,
            lot_number='EXPIRED',
            expiry_date=date.today() - timedelta(days=1),
        )
        return {
            'tenant': tenant,
            'unit': unit,
            'product': product,
            'branch': branch,
            'source': source,
            'target': target,
            'valid_lot': valid_lot,
            'expired_lot': expired_lot,
        }

    return run_in_tenant(tenant, _create)


@pytest.mark.django_db
def test_requires_lot_and_expiry_for_flagged_product(stock_context):
    ctx = stock_context

    def _test():
        with pytest.raises(InvalidLotError, match='requires a lot'):
            create_receipt(
                ctx['tenant'],
                ctx['branch'],
                ctx['product'],
                ctx['source'],
                1,
                ctx['unit'],
                1,
                idempotency_key='receipt-no-lot',
            )

        lot_without_expiry = StockLot.all_objects.create(
            tenant=ctx['tenant'],
            product=ctx['product'],
            lot_number='NOEXP',
        )
        with pytest.raises(InvalidLotError, match='requires expiry'):
            create_receipt(
                ctx['tenant'],
                ctx['branch'],
                ctx['product'],
                ctx['source'],
                1,
                ctx['unit'],
                1,
                lot=lot_without_expiry,
                idempotency_key='receipt-no-expiry',
            )

    run_in_tenant(ctx['tenant'], _test)


@pytest.mark.django_db
def test_common_issue_blocks_expired_lot_but_adjustment_can_write_off(stock_context):
    ctx = stock_context

    def _test():
        create_adjustment(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            3,
            ctx['unit'],
            1,
            lot=ctx['expired_lot'],
            idempotency_key='expired-admin-entry',
            reason='authorized expired lot write-off preparation',
            allow_expired_lot=True,
        )

        with pytest.raises(ExpiredLotError):
            create_issue(
                ctx['tenant'],
                ctx['branch'],
                ctx['product'],
                ctx['source'],
                1,
                ctx['unit'],
                1,
                lot=ctx['expired_lot'],
                idempotency_key='expired-common-issue',
            )

        create_adjustment(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            -1,
            ctx['unit'],
            1,
            lot=ctx['expired_lot'],
            idempotency_key='expired-admin-write-off',
            reason='authorized expired lot write-off',
            allow_expired_lot=True,
        )
        assert get_stock_balance(
            ctx['tenant'], ctx['product'], ctx['source'], ctx['expired_lot']
        ) == Decimal('2')

    run_in_tenant(ctx['tenant'], _test)


@pytest.mark.django_db
def test_identical_replay_returns_original_and_changed_payload_conflicts(stock_context):
    ctx = stock_context

    def _test():
        first = create_receipt(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            5,
            ctx['unit'],
            1,
            lot=ctx['valid_lot'],
            idempotency_key='idem-receipt',
        )
        replay = create_receipt(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            5,
            ctx['unit'],
            1,
            lot=ctx['valid_lot'],
            idempotency_key='idem-receipt',
        )
        assert replay.id == first.id
        assert StockMovement.all_objects.filter(operation=first).count() == 1

        with pytest.raises(DuplicateIdempotencyKey):
            create_receipt(
                ctx['tenant'],
                ctx['branch'],
                ctx['product'],
                ctx['source'],
                6,
                ctx['unit'],
                1,
                lot=ctx['valid_lot'],
                idempotency_key='idem-receipt',
            )

    run_in_tenant(ctx['tenant'], _test)


@pytest.mark.django_db
def test_transfer_is_atomic_and_reversal_is_unique(stock_context):
    ctx = stock_context

    def _test():
        receipt = create_receipt(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            4,
            ctx['unit'],
            1,
            lot=ctx['valid_lot'],
            idempotency_key='transfer-seed',
        )
        assert receipt.status == 'confirmed'

        with pytest.raises(Exception):
            with transaction.atomic():
                create_transfer(
                    ctx['tenant'],
                    ctx['branch'],
                    ctx['branch'],
                    ctx['product'],
                    ctx['source'],
                    ctx['target'],
                    10,
                    ctx['unit'],
                    1,
                    lot=ctx['valid_lot'],
                    idempotency_key='transfer-too-much',
                )
        assert get_stock_balance(
            ctx['tenant'], ctx['product'], ctx['source'], ctx['valid_lot']
        ) == Decimal('4')
        assert get_stock_balance(
            ctx['tenant'], ctx['product'], ctx['target'], ctx['valid_lot']
        ) == Decimal('0')

        reversal = reverse_operation(receipt, reason='undo', idempotency_key='reverse-1')
        assert reversal.operation_type == 'reversal'
        with pytest.raises(ValueError, match='already reversed'):
            reverse_operation(receipt, reason='again', idempotency_key='reverse-2')

    run_in_tenant(ctx['tenant'], _test)


@pytest.mark.django_db
def test_reconciliation_reports_divergence_without_silent_correction(stock_context):
    ctx = stock_context

    def _test():
        create_receipt(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            2,
            ctx['unit'],
            1,
            lot=ctx['valid_lot'],
            idempotency_key='reconcile-seed',
        )
        balance = StockBalance.all_objects.get(
            tenant=ctx['tenant'],
            product=ctx['product'],
            location=ctx['source'],
            lot=ctx['valid_lot'],
        )
        balance.quantity = Decimal('99')
        balance.save(update_fields=['quantity', 'updated_at'])

        divergences = reconcile_stock_balances(ctx['tenant'])
        assert len(divergences) == 1
        assert divergences[0]['projected_quantity'] == Decimal('99')
        assert divergences[0]['movement_quantity'] == Decimal('2')

        balance.refresh_from_db()
        assert balance.quantity == Decimal('99')

    run_in_tenant(ctx['tenant'], _test)


@pytest.mark.django_db
def test_location_with_history_cannot_be_deleted(stock_context):
    ctx = stock_context

    def _test():
        create_receipt(
            ctx['tenant'],
            ctx['branch'],
            ctx['product'],
            ctx['source'],
            1,
            ctx['unit'],
            1,
            lot=ctx['valid_lot'],
            idempotency_key='delete-history-seed',
        )
        with pytest.raises(ValidationError):
            ctx['source'].delete()

    run_in_tenant(ctx['tenant'], _test)
