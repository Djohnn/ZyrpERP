from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from catalog.models import (
    BranchPrice,
    Category,
    Product,
    ProductCode,
    ProductPrice,
    ProductUnit,
    Unit,
)


class FullCleanModelSerializer(serializers.ModelSerializer):
    """Execute model-level validation for catalog API writes.

    Django REST Framework does not call model.clean() automatically. The
    catalog keeps core business rules there, including same-tenant foreign keys
    and price period overlap checks, so API writes must call full_clean()
    before saving.
    """

    def _full_clean(self, instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            if hasattr(exc, 'message_dict'):
                raise serializers.ValidationError(exc.message_dict) from exc
            raise serializers.ValidationError({'non_field_errors': exc.messages}) from exc

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        self._full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        self._full_clean(instance)
        instance.save()
        return instance


class UnitSerializer(FullCleanModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'symbol', 'name', 'precision', 'is_active', 'version']
        read_only_fields = ['id', 'version']


class CategorySerializer(FullCleanModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'parent', 'is_active', 'version']
        read_only_fields = ['id', 'version']


class ProductSerializer(FullCleanModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'base_unit',
            'requires_lot', 'requires_expiry', 'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']


class ProductUnitSerializer(FullCleanModelSerializer):
    class Meta:
        model = ProductUnit
        fields = [
            'id', 'product', 'unit', 'factor', 'is_active', 'version',
        ]
        read_only_fields = ['id', 'product', 'version']


class ProductCodeSerializer(FullCleanModelSerializer):
    class Meta:
        model = ProductCode
        fields = [
            'id', 'product', 'code_type', 'value', 'is_principal',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'product', 'version']


class ProductPriceSerializer(FullCleanModelSerializer):
    class Meta:
        model = ProductPrice
        fields = [
            'id', 'product', 'amount', 'valid_from', 'valid_to',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'product', 'version']


class BranchPriceSerializer(FullCleanModelSerializer):
    class Meta:
        model = BranchPrice
        fields = [
            'id', 'product', 'branch', 'amount', 'valid_from', 'valid_to',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'product', 'version']
