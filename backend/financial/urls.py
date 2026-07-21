from django.urls import path

from financial.views import (
    CashClosingReportView,
    CashflowReportView,
    FinancialReportView,
    InventoryReportView,
    PendingOperationsReportView,
    SalesReportView,
)

urlpatterns = [
    path('reports/sales/', SalesReportView.as_view(), name='report-sales'),
    path('reports/cash-closing/', CashClosingReportView.as_view(), name='report-cash-closing'),
    path('reports/inventory/', InventoryReportView.as_view(), name='report-inventory'),
    path('reports/financial/', FinancialReportView.as_view(), name='report-financial'),
    path('reports/cashflow/', CashflowReportView.as_view(), name='report-cashflow'),
    path(
        'reports/pending-operations/',
        PendingOperationsReportView.as_view(),
        name='report-pending-operations',
    ),
]
