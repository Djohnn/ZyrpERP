from outbox.models import OutboxMessage


def create_outbox_message(
    event_type,
    aggregate_type,
    aggregate_id,
    payload,
    correlation_id='',
    tenant_id='',
    event_version='1',
):
    return OutboxMessage.objects.create(
        event_type=event_type,
        event_version=event_version,
        aggregate_type=aggregate_type,
        aggregate_id=str(aggregate_id),
        payload=payload,
        correlation_id=correlation_id,
        tenant_id=tenant_id,
    )
