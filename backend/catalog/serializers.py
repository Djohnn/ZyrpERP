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


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'symbol', 'name', 'precision', 'is_active', 'version']
        read_only_fields = ['id', 'version']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'parent', 'is_active', 'version']
        read_only_fields = ['id', 'version']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'base_unit',
            'requires_lot', 'requires_expiry', 'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']


class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = [
            'id', 'product', 'unit', 'factor', 'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']


class ProductCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCode
        fields = [
            'id', 'product', 'code_type', 'value', 'is_principal',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = [
            'id', 'product', 'amount', 'valid_from', 'valid_to',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']


class BranchPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchPrice
        fields = [
            'id', 'product', 'branch', 'amount', 'valid_from', 'valid_to',
            'is_active', 'version',
        ]
        read_only_fields = ['id', 'version']