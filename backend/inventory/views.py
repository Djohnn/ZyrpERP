from django.db import transaction
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventory.models import (
    StockBalance,
    StockLocation,
    StockLot,
    StockMovement,
    StockOperation,
    StockOperationReversal,
)
from inventory.permissions import (
    InventoryCapabilityPermission,
    InventoryLocationsPermission,
)
from inventory.serializers import (
    StockBalanceSerializer,
    StockLocationSerializer,
    StockLotSerializer,
    StockMovementSerializer,
    StockOperationReversalSerializer,
    StockOperationSerializer,
)
from tenancy.permissions import HasActiveTenant, HasVerifiedMFA


class TenantScopedViewSetMixin:
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.version += 1
        instance.save(update_fields=['version'])
        return instance


class StockLocationViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = StockLocationSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        InventoryLocationsPermission,
    ]

    def get_queryset(self):
        return StockLocation.objects.select_related(
            'branch',
            'branch__company',
        ).filter(tenant=self.request.tenant)

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasActiveTenant()]
        if self.action in {'create', 'update', 'partial_update', 'destroy', 'set_primary'}:
            permissions.extend([HasVerifiedMFA(), InventoryLocationsPermission()])
        else:
            permissions.append(InventoryLocationsPermission())
        return permissions

    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        location = self.get_object()
        with transaction.atomic():
            StockLocation.all_objects.filter(
                tenant=request.tenant,
                branch=location.branch,
                is_primary=True,
                is_active=True,
            ).exclude(pk=location.pk).update(is_primary=False)
            location.is_primary = True
            location.version += 1
            location.save(update_fields=['is_primary', 'version', 'updated_at'])
        return Response({'detail': 'Local definido como principal.'})


class StockLotViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = StockLotSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        InventoryCapabilityPermission,
    ]

    def get_queryset(self):
        return StockLot.objects.select_related('product').filter(tenant=self.request.tenant)

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasActiveTenant()]
        if self.action in {'create', 'update', 'partial_update', 'destroy', 'deactivate'}:
            permissions.append(HasVerifiedMFA())
        permissions.append(InventoryCapabilityPermission())
        return permissions

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        lot = self.get_object()
        lot.is_active = False
        lot.version += 1
        lot.save(update_fields=['is_active', 'version', 'updated_at'])
        return Response({'detail': 'Lote desativado.'})

    @action(detail=False, methods=['get'])
    def expired(self, request):
        from django.utils import timezone

        lots = self.get_queryset().filter(
            expiry_date__lt=timezone.now().date(),
            is_active=True,
        ).order_by('expiry_date')
        serializer = self.get_serializer(lots, many=True)
        return Response(serializer.data)


class StockOperationViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = StockOperationSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        InventoryCapabilityPermission,
    ]

    def get_queryset(self):
        return StockOperation.objects.select_related('branch', 'actor').filter(
            tenant=self.request.tenant,
        ).prefetch_related('movements')

    def get_permissions(self):
        permissions = [IsAuthenticated(), HasActiveTenant()]
        if self.action in {'create', 'update', 'partial_update', 'destroy', 'confirm'}:
            permissions.append(HasVerifiedMFA())
        permissions.append(InventoryCapabilityPermission())
        return permissions

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, actor=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        operation = self.get_object()
        if operation.status != 'draft':
            return Response(
                {'detail': 'Apenas operacoes em rascunho podem ser confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        operation.status = 'confirmed'
        operation.version += 1
        operation.save(update_fields=['status', 'version', 'updated_at'])
        return Response({'detail': 'Operacao confirmada.', 'id': str(operation.id)})


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockMovementSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        InventoryCapabilityPermission,
    ]

    def get_queryset(self):
        return StockMovement.objects.select_related(
            'operation',
            'product',
            'location',
            'lot',
            'unit',
        ).filter(tenant=self.request.tenant)


class StockBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockBalanceSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        InventoryCapabilityPermission,
    ]

    def get_queryset(self):
        queryset = StockBalance.objects.select_related(
            'product',
            'location',
            'location__branch',
            'lot',
        ).filter(tenant=self.request.tenant)
        product_id = self.request.query_params.get('product')
        branch_id = self.request.query_params.get('branch')
        location_id = self.request.query_params.get('location')
        lot_id = self.request.query_params.get('lot')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if branch_id:
            queryset = queryset.filter(location__branch_id=branch_id)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if lot_id:
            queryset = queryset.filter(lot_id=lot_id)
        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset().filter(quantity__gt=0)
        totals = queryset.aggregate(
            total_quantity=Sum('quantity'),
            total_reserved=Sum('reserved'),
        )
        total_quantity = totals['total_quantity'] or 0
        total_reserved = totals['total_reserved'] or 0
        return Response(
            {
                'total_items': queryset.count(),
                'total_quantity': total_quantity,
                'total_reserved': total_reserved,
                'total_available': total_quantity - total_reserved,
            }
        )


class StockOperationReversalViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = StockOperationReversalSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveTenant,
        HasVerifiedMFA,
        InventoryCapabilityPermission,
    ]

    def get_queryset(self):
        return StockOperationReversal.objects.select_related(
            'original_operation',
            'reversal_operation',
        ).filter(tenant=self.request.tenant)
