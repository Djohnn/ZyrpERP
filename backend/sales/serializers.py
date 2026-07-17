from decimal import Decimal

from rest_framework import serializers

from sales.models import CashMovement, CashSession, Sale, SaleItem, SalePayment


class CashMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashMovement
        fields = [
            'id', 'movement_type', 'amount', 'payment_method', 'reference',
            'notes', 'created_at',
        ]
        read_only_fields = fields


class CashSessionSerializer(serializers.ModelSerializer):
    movements = CashMovementSerializer(many=True, read_only=True)

    class Meta:
        model = CashSession
        fields = [
            'id', 'branch', 'operator', 'status', 'opening_amount',
            'expected_amount', 'closing_amount', 'opened_at', 'closed_at',
            'version', 'movements',
        ]
        read_only_fields = fields


class OpenCashSessionSerializer(serializers.Serializer):
    branch = serializers.UUIDField()
    opening_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class CloseCashSessionSerializer(serializers.Serializer):
    closing_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'unit', 'stock_operation', 'quantity', 'factor',
            'unit_price', 'discount_amount', 'line_total',
        ]
        read_only_fields = fields


class SalePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayment
        fields = ['id', 'method', 'amount', 'reference']
        read_only_fields = fields


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'branch', 'cash_session', 'operator', 'status',
            'gross_total', 'discount_total', 'net_total', 'created_at',
            'version', 'items', 'payments',
        ]
        read_only_fields = fields


class CounterSaleItemInputSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    unit = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=18, decimal_places=6)
    factor = serializers.DecimalField(max_digits=18, decimal_places=6)
    discount_amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        required=False,
        default=Decimal('0'),
    )


class CounterSalePaymentInputSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=SalePayment.METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    reference = serializers.CharField(required=False, allow_blank=True, default='')


class CounterSaleSerializer(serializers.Serializer):
    branch = serializers.UUIDField()
    stock_location = serializers.UUIDField()
    items = CounterSaleItemInputSerializer(many=True)
    payments = CounterSalePaymentInputSerializer(many=True)
