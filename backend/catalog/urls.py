from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import (
    BranchPriceViewSet,
    CategoryViewSet,
    EffectivePriceView,
    ProductCodeViewSet,
    ProductPriceViewSet,
    ProductUnitViewSet,
    ProductViewSet,
    UnitViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('units', UnitViewSet, basename='unit')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'products/<uuid:product_id>/effective-price/',
        EffectivePriceView.as_view(),
        name='product-effective-price',
    ),
    path(
        'products/<uuid:product_pk>/units/',
        ProductUnitViewSet.as_view({
            'get': 'list', 'post': 'create',
        }),
        name='product-unit-list',
    ),
    path(
        'products/<uuid:product_pk>/units/<uuid:pk>/',
        ProductUnitViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='product-unit-detail',
    ),
    path(
        'products/<uuid:product_pk>/codes/',
        ProductCodeViewSet.as_view({
            'get': 'list', 'post': 'create',
        }),
        name='product-code-list',
    ),
    path(
        'products/<uuid:product_pk>/codes/<uuid:pk>/',
        ProductCodeViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='product-code-detail',
    ),
    path(
        'products/<uuid:product_pk>/prices/',
        ProductPriceViewSet.as_view({
            'get': 'list', 'post': 'create',
        }),
        name='product-price-list',
    ),
    path(
        'products/<uuid:product_pk>/prices/<uuid:pk>/',
        ProductPriceViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='product-price-detail',
    ),
    path(
        'products/<uuid:product_pk>/branch-prices/',
        BranchPriceViewSet.as_view({
            'get': 'list', 'post': 'create',
        }),
        name='branch-price-list',
    ),
    path(
        'products/<uuid:product_pk>/branch-prices/<uuid:pk>/',
        BranchPriceViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='branch-price-detail',
    ),
]