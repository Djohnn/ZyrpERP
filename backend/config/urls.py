from django.contrib import admin
from django.urls import include, path

from .views import health

urlpatterns = [
    path('health/', health, name='health'),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('tenancy.urls')),
    path('api/v1/', include('catalog.urls')),
    path('admin/', admin.site.urls),
]
