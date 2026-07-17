from decimal import Decimal

from django.db import transaction

from audit.services import create_audit_record
from inventory.models import (
    StockBalance,
    StockMovement,
    StockOperation,
    StockOperationReversal,
)
from outbox.services import create_outbox_message


class InsufficientStock(Exception):
    pass


class InvalidLotError(Exception):
    pass


class DuplicateIdempotencyKey(Exception):
    pass


def _base_quantity(quantity, factor):
    return Decimal(str(quantity)) * Decimal(str(factor))


def _get_balance(tenant, product, location, lot=None, for_update=False):
    queryset = StockBalance.all_objects
    if for_update:
        queryset = queryset.select_for_update()
    filters = {
        'tenant': tenant,
        'product': product,
        'location': location,
        'lot': lot,
    }
    balance, _ = queryset.get_or_create(
        **filters,
        defaults={'quantity': Decimal('0'), 'reserved': Decimal('0')},
    )
    return balance


def _apply_balance_delta(tenant, product, location, quantity, lot=None):
    balance = _get_balance(tenant, product, location, lot, for_update=True)
    next_quantity = balance.quantity + quantity
    if next_quantity < 0:
        raise InsufficientStock(
            f'Insufficient stock. Available: {balance.quantity}, required: {abs(quantity)}'
        )
    balance.quantity = next_quantity
    balance.version += 1
    balance.full_clean()
    balance.save(update_fields=['quantity', 'version', 'updated_at'])
    return balance


def get_available_stock(tenant, product, location, lot=None, exclude_reserved=False):
    balance = StockBalance.all_objects.filter(
        tenant=tenant,
        product=product,
        location=location,
        lot=lot,
    ).first()
    if balance is None:
        return Decimal('0')
    if exclude_reserved:
        return max(balance.available, Decimal('0'))
    return balance.quantity


def reserve_stock(tenant, product, location, quantity, lot=None):
    balance = _get_balance(tenant, product, location, lot, for_update=True)
    quantity = Decimal(str(quantity))
    if balance.reserved + quantity > balance.quantity:
        raise InsufficientStock(
            f'Cannot reserve {quantity}. Available: {balance.available}'
        )
    balance.reserved += quantity
    balance.version += 1
    balance.full_clean()
    balance.save(update_fields=['reserved', 'version', 'updated_at'])
    return balance


def release_reservation(tenant, product, location, quantity, lot=None):
    balance = _get_balance(tenant, product, location, lot, for_update=True)
    quantity = Decimal(str(quantity))
    balance.reserved = max(balance.reserved - quantity, Decimal('0'))
    balance.version += 1
    balance.full_clean()
    balance.save(update_fields=['reserved', 'version', 'updated_at'])
    return balance


def _emit_inventory_event(operation, event_type, actor=None):
    create_audit_record(
        actor=actor,
        action=event_type,
        resource_type='StockOperation',
        resource_id=str(operation.id),
        detail={
            'operation_type': operation.operation_type,
            'status': operation.status,
        },
        correlation_id=operation.idempotency_key,
        tenant_id=operation.tenant_id,
    )
    create_outbox_message(
        event_type=event_type,
        aggregate_type='StockOperation',
        aggregate_id=str(operation.id),
        payload={
            'operation_id': str(operation.id),
            'operation_type': operation.operation_type,
            'status': operation.status,
        },
        correlation_id=operation.idempotency_key,
        tenant_id=operation.tenant_id,
    )


def _find_idempotent_operation(tenant, idempotency_key):
    if not idempotency_key:
        return None
    return StockOperation.all_objects.filter(
        tenant=tenant,
        idempotency_key=idempotency_key,
    ).first()


@transaction.atomic
def create_stock_movement(
    *,
    operation,
    product,
    location,
    direction,
    quantity,
    unit,
    factor=1,
    lot=None,
    unit_cost=None,
    notes='',
):
    base_quantity = _base_quantity(quantity, factor)
    if base_quantity <= 0:
        raise ValueError('Quantity must be positive')
    if lot and lot.product_id != product.id:
        raise InvalidLotError('Lot must belong to the same product.')

    movement = StockMovement.all_objects.create(
        tenant=operation.tenant,
        operation=operation,
        product=product,
        location=location,
        lot=lot,
        direction=direction,
        quantity=base_quantity,
        unit=unit,
        factor=factor,
        unit_cost=unit_cost,
        notes=notes,
    )
    delta = base_quantity if direction == 'in' else -base_quantity
    _apply_balance_delta(operation.tenant, product, location, delta, lot)
    return movement


@transaction.atomic
def create_operation(
    *,
    tenant,
    operation_type,
    branch=None,
    idempotency_key='',
    actor=None,
    reason='',
    status='confirmed',
):
    existing = _find_idempotent_operation(tenant, idempotency_key)
    if existing:
        return existing
    operation = StockOperation.all_objects.create(
        tenant=tenant,
        operation_type=operation_type,
        branch=branch,
        idempotency_key=idempotency_key or '',
        actor=actor,
        reason=reason,
        status=status,
    )
    _emit_inventory_event(operation, f'inventory.{operation_type}.created', actor)
    return operation


def create_receipt(
    tenant,
    branch,
    product,
    location,
    quantity,
    unit,
    factor,
    lot=None,
    unit_cost=None,
    idempotency_key=None,
    actor=None,
    reason='',
):
    operation = create_operation(
        tenant=tenant,
        operation_type='receipt',
        branch=branch,
        idempotency_key=idempotency_key or '',
        actor=actor,
        reason=reason,
    )
    if not operation.movements.exists():
        create_stock_movement(
            operation=operation,
            product=product,
            location=location,
            direction='in',
            quantity=quantity,
            unit=unit,
            factor=factor,
            lot=lot,
            unit_cost=unit_cost,
        )
    return operation


def create_issue(
    tenant,
    branch,
    product,
    location,
    quantity,
    unit,
    factor,
    idempotency_key=None,
    actor=None,
    reason='',
    unit_cost=None,
):
    operation = create_operation(
        tenant=tenant,
        operation_type='issue',
        branch=branch,
        idempotency_key=idempotency_key or '',
        actor=actor,
        reason=reason,
    )
    if not operation.movements.exists():
        create_stock_movement(
            operation=operation,
            product=product,
            location=location,
            direction='out',
            quantity=quantity,
            unit=unit,
            factor=factor,
            unit_cost=unit_cost,
        )
    return operation


def create_adjustment(
    tenant,
    branch,
    product,
    location,
    quantity,
    unit,
    factor,
    idempotency_key=None,
    actor=None,
    reason='',
    unit_cost=None,
):
    quantity = Decimal(str(quantity))
    direction = 'in' if quantity > 0 else 'out'
    operation = create_operation(
        tenant=tenant,
        operation_type='adjustment',
        branch=branch,
        idempotency_key=idempotency_key or '',
        actor=actor,
        reason=reason,
    )
    if not operation.movements.exists():
        create_stock_movement(
            operation=operation,
            product=product,
            location=location,
            direction=direction,
            quantity=abs(quantity),
            unit=unit,
            factor=factor,
            unit_cost=unit_cost,
        )
    return operation


def create_transfer(
    tenant,
    source_branch,
    target_branch,
    product,
    source_location,
    target_location,
    quantity,
    unit,
    factor,
    idempotency_key=None,
    actor=None,
    reason='',
):
    operation = create_operation(
        tenant=tenant,
        operation_type='transfer',
        branch=source_branch,
        idempotency_key=idempotency_key or '',
        actor=actor,
        reason=reason or f'Transfer to {target_branch}',
    )
    if not operation.movements.exists():
        create_stock_movement(
            operation=operation,
            product=product,
            location=source_location,
            direction='out',
            quantity=quantity,
            unit=unit,
            factor=factor,
        )
        create_stock_movement(
            operation=operation,
            product=product,
            location=target_location,
            direction='in',
            quantity=quantity,
            unit=unit,
            factor=factor,
        )
    return operation


@transaction.atomic
def reverse_operation(operation, reason='', idempotency_key='', actor=None):
    if operation.status != 'confirmed':
        raise ValueError('Only confirmed operations can be reversed.')
    if operation.reversals.exists():
        raise ValueError('Operation already reversed.')

    reversal = create_operation(
        tenant=operation.tenant,
        operation_type='reversal',
        branch=operation.branch,
        idempotency_key=idempotency_key,
        actor=actor,
        reason=reason,
    )
    for movement in operation.movements.all():
        create_stock_movement(
            operation=reversal,
            product=movement.product,
            location=movement.location,
            lot=movement.lot,
            direction='out' if movement.direction == 'in' else 'in',
            quantity=movement.quantity,
            unit=movement.unit,
            factor=1,
            unit_cost=movement.unit_cost,
            notes=f'Reversal of {operation.id}',
        )
    StockOperationReversal.all_objects.create(
        tenant=operation.tenant,
        original_operation=operation,
        reversal_operation=reversal,
        reason=reason,
    )
    operation.status = 'reversed'
    operation.version += 1
    operation.save(update_fields=['status', 'version', 'updated_at'])
    return reversal


def process_operation(operation):
    _emit_inventory_event(operation, 'inventory.operation.confirmed', operation.actor)
    return operation


def get_stock_balance(tenant, product, location, lot=None):
    balance = StockBalance.all_objects.filter(
        tenant=tenant,
        product=product,
        location=location,
        lot=lot,
    ).first()
    return balance.quantity if balance else Decimal('0')
