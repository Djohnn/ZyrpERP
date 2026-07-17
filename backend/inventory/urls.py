from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory.views import (
    StockBalanceViewSet,
    StockLocationViewSet,
    StockLotViewSet,
    StockMovementViewSet,
    StockOperationReversalViewSet,
    StockOperationViewSet,
)

router = DefaultRouter()
router.register('stock-locations', StockLocationViewSet, basename='stocklocation')
router.register('stock-lots', StockLotViewSet, basename='stocklot')
router.register('stock-operations', StockOperationViewSet, basename='stockoperation')
router.register('stock-movements', StockMovementViewSet, basename='stockmovement')
router.register('stock-balances', StockBalanceViewSet, basename='stockbalance')
router.register(
    'stock-operation-reversals',
    StockOperationReversalViewSet,
    basename='stockoperationreversal',
)

urlpatterns = [
    path('', include(router.urls)),
]
