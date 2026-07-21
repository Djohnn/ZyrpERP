from django.contrib import admin
from django.urls import include, path

from .views import health

urlpatterns = [
    path('health/', health, name='health'),
    path('api/v1/health/', health, name='api-health'),
    path('api/v1/monitoring/', include('monitoring.urls')),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('tenancy.urls')),
    path('api/v1/', include('catalog.urls')),
    path('api/v1/', include('inventory.urls')),
    path('api/v1/', include('sales.urls')),
    path('api/v1/', include('fiscal.urls')),
    path('admin/', admin.site.urls),
]
