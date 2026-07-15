from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import (
    BranchPrice,
    Category,
    Product,
    ProductCode,
    ProductPrice,
    ProductUnit,
    Unit,
)
from catalog.permissions import CatalogCapabilityPermission, PricingCapabilityPermission
from catalog.serializers import (
    BranchPriceSerializer,
    CategorySerializer,
    ProductCodeSerializer,
    ProductPriceSerializer,
    ProductSerializer,
    ProductUnitSerializer,
    UnitSerializer,
)
from catalog.services.pricing import PriceNotAvailable, resolve_effective_price
from tenancy.permissions import HasActiveTenant, HasVerifiedMFA


def _resolve_effective_price_response(request, product):
    branch_id = request.query_params.get('branch_id')
    if not branch_id:
        return Response(
            {
                'type': 'about:blank',
                'title': 'Bad Request',
                'status': 400,
                'detail': 'branch_id is required.',
                'code': 'VALIDATION_FAILED',
            },
            status=400,
            content_type='application/problem+json',
        )
    from tenancy.models import Branch

    branch = get_object_or_404(Branch, id=branch_id, tenant=request.tenant)
    at = request.query_params.get('at')
    if at:
        from django.utils.dateparse import parse_datetime

        at_dt = parse_datetime(at)
        if at_dt is None:
            return Response(
                {
                    'type': 'about:blank',
                    'title': 'Bad Request',
                    'status': 400,
                    'detail': 'Invalid "at" datetime.',
                    'code': 'VALIDATION_FAILED',
                },
                status=400,
                content_type='application/problem+json',
            )
    else:
        from django.utils import timezone

        at_dt = timezone.now()
    try:
        price = resolve_effective_price(
            product=product, branch=branch, at=at_dt,
        )
    except PriceNotAvailable:
        return Response(
            {
                'type': 'about:blank',
                'title': 'Not Found',
                'status': 404,
                'detail': 'No active price for this product.',
                'code': 'CATALOG_PRICE_NOT_AVAILABLE',
            },
            status=404,
            content_type='application/problem+json',
        )
    source = 'branch' if isinstance(price, BranchPrice) else 'tenant'
    data = {
        'id': str(price.id),
        'amount': str(price.amount),
        'currency': 'BRL',
        'source': source,
        'valid_from': price.valid_from.isoformat() if price.valid_from else None,
        'valid_to': price.valid_to.isoformat() if price.valid_to else None,
    }
    return Response(data)


class CatalogCursorPagination(CursorPagination):
    ordering = '-created_at'
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CatalogViewSetBase(viewsets.ModelViewSet):
    pagination_class = CatalogCursorPagination
    permission_classes = [
        IsAuthenticated, HasActiveTenant, HasVerifiedMFA,
        CatalogCapabilityPermission,
    ]

    def get_queryset(self):
        qs = self.queryset.model.objects.filter(tenant=self.request.tenant)
        search = self.request.query_params.get('search')
        if search and hasattr(self.model, 'name'):
            qs = qs.filter(name__icontains=search)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if_match = request.headers.get('If-Match')
        if if_match is not None and str(instance.version) != if_match:
            return Response(
                {
                    'type': 'about:blank',
                    'title': 'Conflict',
                    'status': 409,
                    'detail': 'Version mismatch.',
                    'code': 'CONFLICT_VERSION_MISMATCH',
                },
                status=status.HTTP_409_CONFLICT,
                content_type='application/problem+json',
            )
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.version += 1
        instance.save(update_fields=['version'])


class UnitViewSet(CatalogViewSetBase):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class CategoryViewSet(CatalogViewSetBase):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(CatalogViewSetBase):
    queryset = Product.objects.select_related('category', 'base_unit')
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs


class ProductUnitViewSet(CatalogViewSetBase):
    queryset = ProductUnit.objects.select_related('product', 'unit')
    serializer_class = ProductUnitSerializer

    def get_queryset(self):
        return super().get_queryset().filter(product_id=self.kwargs.get('product_pk'))


class ProductCodeViewSet(CatalogViewSetBase):
    queryset = ProductCode.objects.select_related('product')
    serializer_class = ProductCodeSerializer

    def get_queryset(self):
        return super().get_queryset().filter(product_id=self.kwargs.get('product_pk'))


class ProductPriceViewSet(CatalogViewSetBase):
    queryset = ProductPrice.objects.select_related('product')
    serializer_class = ProductPriceSerializer
    permission_classes = [
        IsAuthenticated, HasActiveTenant, HasVerifiedMFA,
        PricingCapabilityPermission,
    ]

    def get_queryset(self):
        return super().get_queryset().filter(product_id=self.kwargs.get('product_pk'))


class BranchPriceViewSet(CatalogViewSetBase):
    queryset = BranchPrice.objects.select_related('product', 'branch')
    serializer_class = BranchPriceSerializer
    permission_classes = [
        IsAuthenticated, HasActiveTenant, HasVerifiedMFA,
        PricingCapabilityPermission,
    ]

    def get_queryset(self):
        return super().get_queryset().filter(product_id=self.kwargs.get('product_pk'))


class EffectivePriceView(APIView):
    permission_classes = [
        IsAuthenticated, HasActiveTenant, HasVerifiedMFA,
        PricingCapabilityPermission,
    ]

    def get(self, request, product_id):
        product = get_object_or_404(
            Product, id=product_id, tenant=request.tenant,
        )
        return _resolve_effective_price_response(request, product)