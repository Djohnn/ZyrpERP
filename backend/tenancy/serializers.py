from rest_framework import serializers

from tenancy.models import Company


class CompanySerializer(serializers.ModelSerializer):
    tenant = serializers.UUIDField(source='tenant_id', read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'tenant', 'name', 'cnpj', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']
