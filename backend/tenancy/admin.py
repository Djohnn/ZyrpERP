from django.contrib import admin

from .models import Branch, Company, Tenant, TenantMembership, UserBranch


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['is_active']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'cnpj', 'is_active']
    search_fields = ['name']
    list_filter = ['tenant', 'is_active']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'is_active']
    search_fields = ['name']
    list_filter = ['company__tenant', 'is_active']


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'is_active']
    list_filter = ['tenant', 'role', 'is_active']


@admin.register(UserBranch)
class UserBranchAdmin(admin.ModelAdmin):
    list_display = ['user', 'branch', 'is_active']
    list_filter = ['branch__company__tenant', 'is_active']
