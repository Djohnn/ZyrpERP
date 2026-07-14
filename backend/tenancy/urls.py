from django.urls import path

from tenancy.views import CompanyDetailView, CompanyListCreateView

app_name = 'tenancy'

urlpatterns = [
    path('companies/', CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<uuid:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]
