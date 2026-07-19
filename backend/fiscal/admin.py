from django.contrib import admin

from fiscal.models import FiscalDocument, FiscalEmitter, FiscalProductConfig


@admin.register(FiscalEmitter)
class FiscalEmitterAdmin(admin.ModelAdmin):
    list_display = [
        'cpf_cnpj',
        'branch',
        'provider',
        'registered_at_provider',
        'registration_source',
        'is_active',
    ]
    list_filter = ['provider', 'registered_at_provider', 'registration_source', 'is_active']
    search_fields = ['cpf_cnpj', 'branch__name']


@admin.register(FiscalProductConfig)
class FiscalProductConfigAdmin(admin.ModelAdmin):
    list_display = ['product', 'cst_icms', 'cst_pis', 'cst_cofins', 'origem', 'is_active']
    list_filter = ['is_active', 'origem']
    search_fields = ['product__sku', 'product__name']


@admin.register(FiscalDocument)
class FiscalDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'sale',
        'status',
        'attempt_number',
        'is_active',
        'provider_document_id',
        'protocol',
        'created_at',
    ]
    list_filter = ['status', 'is_active']
    search_fields = ['sale__id', 'provider_document_id', 'protocol']
    readonly_fields = ['idempotency_key', 'created_at', 'updated_at']
