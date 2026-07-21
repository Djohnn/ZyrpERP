import hashlib
import json

from django.db import transaction

from audit.services import create_audit_record
from outbox.services import create_outbox_message


def _payload_hash(payload):
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


class DuplicateIdempotencyKey(ValueError):
    def __init__(self, existing):
        self.existing = existing
        super().__init__(
            f'Idempotency key "{existing.idempotency_key}" '
            f'already used with a different payload.'
        )


def _build_payload(*, supplier_name, description, amount, due_date):
    return {
        'supplier_name': supplier_name,
        'description': description,
        'amount': str(amount),
        'due_date': str(due_date) if due_date else None,
    }


@transaction.atomic
def create_payable(
    *, tenant, supplier_name, description, amount,
    due_date=None, idempotency_key='', actor=None,
):
    from financial.models import Payable

    fingerprint = _payload_hash(
        _build_payload(
            supplier_name=supplier_name,
            description=description,
            amount=amount,
            due_date=due_date,
        )
    )

    if idempotency_key:
        existing = Payable.all_objects.filter(
            tenant=tenant, idempotency_key=idempotency_key,
        ).first()
        if existing:
            if existing.payload_hash != fingerprint:
                raise DuplicateIdempotencyKey(existing)
            return existing

    payable = Payable.all_objects.create(
        tenant=tenant,
        supplier_name=supplier_name,
        description=description,
        amount=amount,
        due_date=due_date,
        idempotency_key=idempotency_key,
        payload_hash=fingerprint,
    )

    create_audit_record(
        action='financial.payable.created',
        resource_type='payable',
        resource_id=payable.id,
        detail={
            'supplier_name': supplier_name,
            'amount': str(amount),
        },
        actor=actor,
        correlation_id=idempotency_key,
        tenant_id=str(tenant.id),
    )
    create_outbox_message(
        event_type='financial.payable.created',
        aggregate_type='payable',
        aggregate_id=payable.id,
        payload={'supplier_name': supplier_name, 'amount': str(amount)},
        correlation_id=idempotency_key,
        tenant_id=str(tenant.id),
    )

    return payable
