from rest_framework import serializers

from tenancy.models import Invitation, TenantMembership, TenantMFAPolicy


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'role', 'expires_at', 'accepted_at', 'created_at']
        read_only_fields = ['id', 'expires_at', 'accepted_at', 'created_at']


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=300)


class MembershipSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TenantMembership
        fields = ['id', 'email', 'role', 'is_active']
        read_only_fields = ['id', 'email']


class MFAPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantMFAPolicy
        fields = ['allow_totp', 'allow_email']
