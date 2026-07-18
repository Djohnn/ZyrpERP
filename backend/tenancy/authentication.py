import logging
import uuid

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from tenancy.models import Device, TenantMembership

logger = logging.getLogger(__name__)


class DeviceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        raw = validated_token.get('device_id')
        if not raw:
            logger.warning('JWT missing device_id claim')
            raise AuthenticationFailed('No device_id in token')

        try:
            device_id = uuid.UUID(raw)
        except (ValueError, TypeError):
            logger.warning('Invalid device_id in JWT: %s', raw)
            raise AuthenticationFailed('Invalid device_id format')

        try:
            device = Device.all_objects.select_related('registered_by').get(id=device_id)
        except Device.DoesNotExist:
            logger.warning('Device not found: %s', device_id)
            raise AuthenticationFailed('Device not found')

        logger.info('Device found: %s (registered_by=%s)', device.id, device.registered_by)

        if device.registered_by and device.registered_by.is_active:
            return device.registered_by

        membership = (
            TenantMembership.objects.filter(tenant=device.tenant, is_active=True)
            .select_related('user')
            .first()
        )
        if membership and membership.user.is_active:
            return membership.user

        raise AuthenticationFailed('Device has no registered user and no active members found')
