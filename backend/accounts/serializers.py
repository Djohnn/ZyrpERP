from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=12)
    tenant_name = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)
    branch_name = serializers.CharField(max_length=200)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=300)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(TokenSerializer):
    password = serializers.CharField(write_only=True, min_length=12)


class TenantSelectionSerializer(serializers.Serializer):
    tenant_id = serializers.UUIDField()


class TOTPConfirmationSerializer(serializers.Serializer):
    device_id = serializers.UUIDField()
    code = serializers.RegexField(r'^\d{6}$')


class EmailChallengeSerializer(serializers.Serializer):
    challenge_id = serializers.UUIDField()
    code = serializers.RegexField(r'^\d{6}$')
