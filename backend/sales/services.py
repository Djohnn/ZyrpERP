import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from audit.services import create_audit_record
from catalog.services.pricing import resolve_effective_price
from inventory.services import create_issue
from outbox.services import create_outbox_message
from sales.models import CashMovement, CashSession, Sale, SaleItem, SalePayment


class DuplicateIdempotencyKey(Exception):
    pass


class CashSessionRequired(Exception):
    pass


class OpenCashSessionExists(Exception):
    pass


class PaymentMismatch(Exception):
    pass


class EmptySale(Exception):
    pass


def _money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _json_default(value):
    if hasattr(value, 'id'):
        return str(value.id)
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _payload_hash(payload):
    encoded = json.dumps(payload, sort_keys=True, default=_json_default).encode()
    return hashlib.sha256(encoded).hexdigest()


def _emit_sales_event(*, sale, event_type, actor=None):
    create_audit_record(
        actor=actor,
        action=event_type,
        resource_type='Sale',
        resource_id=str(sale.id),
        detail={
            'status': sale.status,
            'gross_total': str(sale.gross_total),
            'net_total': str(sale.net_total),
        },
        correlation_id=sale.idempotency_key,
        tenant_id=sale.tenant_id,
    )
    create_outbox_message(
        event_type=event_type,
        aggregate_type='Sale',
        aggregate_id=str(sale.id),
        payload={
            'sale_id': str(sale.id),
            'status': sale.status,
            'gross_total': str(sale.gross_total),
            'net_total': str(sale.net_total),
        },
        correlation_id=sale.idempotency_key,
        tenant_id=sale.tenant_id,
    )


def _open_cash_session_for(tenant, branch, operator):
    return CashSession.all_objects.filter(
        tenant=tenant,
        branch=branch,
        operator=operator,
        status='open',
    ).first()


@transaction.atomic
def open_cash_session(*, tenant, branch, operator, opening_amount, idempotency_key):
    if not idempotency_key:
        raise ValueError('Idempotency-Key is required.')
    payload = {
        'branch': branch,
        'operator': operator,
        'opening_amount': str(opening_amount),
    }
    fingerprint = _payload_hash(payload)
    existing = CashSession.all_objects.filter(
        tenant=tenant,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        if existing.payload_hash != fingerprint:
            raise DuplicateIdempotencyKey(
                'Idempotency key already used with a different payload.'
            )
        return existing
    if _open_cash_session_for(tenant, branch, operator):
        raise OpenCashSessionExists('There is already an open cash session.')

    amount = _money(opening_amount)
    session = CashSession.all_objects.create(
        tenant=tenant,
        branch=branch,
        operator=operator,
        opening_amount=amount,
        expected_amount=amount,
        idempotency_key=idempotency_key,
        payload_hash=fingerprint,
    )
    CashMovement.all_objects.create(
        tenant=tenant,
        cash_session=session,
        movement_type='opening',
        amount=amount,
        notes='Opening balance',
    )
    return session


@transaction.atomic
def close_cash_session(*, cash_session, closing_amount, idempotency_key):
    if not idempotency_key:
        raise ValueError('Idempotency-Key is required.')
    if cash_session.status == 'closed':
        return cash_session
    cash_session.status = 'closed'
    cash_session.closing_amount = _money(closing_amount)
    cash_session.closed_at = timezone.now()
    cash_session.version += 1
    cash_session.save(
        update_fields=[
            'status',
            'closing_amount',
            'closed_at',
            'version',
            'updated_at',
        ]
    )
    return cash_session


def _normalize_item(item):
    return {
        'product': item['product'],
        'unit': item['unit'],
        'quantity': Decimal(str(item['quantity'])),
        'factor': Decimal(str(item.get('factor', 1))),
        'discount_amount': _money(item.get('discount_amount', 0)),
    }


def _normalize_payment(payment):
    return {
        'method': payment['method'],
        'amount': _money(payment['amount']),
        'reference': payment.get('reference', ''),
    }


@transaction.atomic
def create_counter_sale(
    *,
    tenant,
    branch,
    operator,
    stock_location,
    items,
    payments,
    idempotency_key,
):
    if not idempotency_key:
        raise ValueError('Idempotency-Key is required.')
    if not items:
        raise EmptySale('Sale must have at least one item.')
    if not payments:
        raise PaymentMismatch('Sale must have at least one payment.')

    normalized_items = [_normalize_item(item) for item in items]
    normalized_payments = [_normalize_payment(payment) for payment in payments]
    payload = {
        'branch': branch,
        'operator': operator,
        'stock_location': stock_location,
        'items': normalized_items,
        'payments': normalized_payments,
    }
    fingerprint = _payload_hash(payload)
    existing = Sale.all_objects.filter(
        tenant=tenant,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        if existing.payload_hash != fingerprint:
            raise DuplicateIdempotencyKey(
                'Idempotency key already used with a different payload.'
            )
        return existing

    cash_session = _open_cash_session_for(tenant, branch, operator)
    if cash_session is None:
        raise CashSessionRequired('An open cash session is required.')

    lines = []
    gross_total = Decimal('0.00')
    discount_total = Decimal('0.00')
    for item in normalized_items:
        price = resolve_effective_price(
            product=item['product'],
            branch=branch,
        )
        unit_price = Decimal(str(price.amount))
        line_gross = _money(item['quantity'] * unit_price)
        line_total = _money(line_gross - item['discount_amount'])
        if line_total < 0:
            raise ValueError('Line total cannot be negative.')
        gross_total += line_gross
        discount_total += item['discount_amount']
        lines.append({**item, 'unit_price': unit_price, 'line_total': line_total})

    gross_total = _money(gross_total)
    discount_total = _money(discount_total)
    net_total = _money(gross_total - discount_total)
    payment_total = _money(sum(payment['amount'] for payment in normalized_payments))
    if payment_total != net_total:
        raise PaymentMismatch('Payment total must match sale net total.')

    sale = Sale.all_objects.create(
        tenant=tenant,
        branch=branch,
        cash_session=cash_session,
        operator=operator,
        gross_total=gross_total,
        discount_total=discount_total,
        net_total=net_total,
        idempotency_key=idempotency_key,
        payload_hash=fingerprint,
    )
    for index, line in enumerate(lines, start=1):
        stock_operation = create_issue(
            tenant,
            branch,
            line['product'],
            stock_location,
            line['quantity'],
            line['unit'],
            line['factor'],
            idempotency_key=f'{idempotency_key}:stock:{index}',
            actor=operator,
            reason=f'Sale {sale.id}',
        )
        SaleItem.all_objects.create(
            tenant=tenant,
            sale=sale,
            product=line['product'],
            unit=line['unit'],
            stock_operation=stock_operation,
            quantity=line['quantity'],
            factor=line['factor'],
            unit_price=line['unit_price'],
            discount_amount=line['discount_amount'],
            line_total=line['line_total'],
        )
    for payment in normalized_payments:
        SalePayment.all_objects.create(
            tenant=tenant,
            sale=sale,
            method=payment['method'],
            amount=payment['amount'],
            reference=payment['reference'],
        )
        CashMovement.all_objects.create(
            tenant=tenant,
            cash_session=cash_session,
            movement_type='sale_payment',
            amount=payment['amount'],
            payment_method=payment['method'],
            reference=str(sale.id),
            notes='Sale payment',
        )
    cash_session.expected_amount = _money(cash_session.expected_amount + net_total)
    cash_session.version += 1
    cash_session.save(update_fields=['expected_amount', 'version', 'updated_at'])
    _emit_sales_event(sale=sale, event_type='sales.sale.confirmed', actor=operator)
    return sale
