from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=12)
    tenant_name = serializers.CharField(max_length=200)
    company_name = serializers.CharField(max_length=200)
    branch_name = serializers.CharField(max_length=200)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=300)
