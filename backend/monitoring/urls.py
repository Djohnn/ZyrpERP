from django.urls import path

from monitoring.views import (
    HealthCheckView,
    MetricsResetView,
    MetricsView,
    ReadinessView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('ready/', ReadinessView.as_view(), name='ready'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('metrics/reset/', MetricsResetView.as_view(), name='metrics-reset'),
]