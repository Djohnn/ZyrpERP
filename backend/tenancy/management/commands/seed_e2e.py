import hashlib
import uuid

from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from catalog.models import Category, Product, ProductPrice, Unit
from inventory.models import StockLocation
from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Branch, Company, Device, Tenant

User = get_user_model()

E2E_API_KEY = 'e2e-test-key-2026'
E2E_PASSWORD = 'e2e-test-pwd-2026'  # noqa: S105


class Command(BaseCommand):
    help = 'Cria dados de teste E2E para o PDV (dispositivo, produto, local de estoque).'

    def handle(self, *args, **options):
        password = config('SEED_ADMIN_PASSWORD', default=E2E_PASSWORD)

        admin_user, created = User.objects.get_or_create(email='e2e@zyrp.local')
        if created:
            admin_user.is_staff = True
            admin_user.is_superuser = True
        admin_user.set_password(password)
        admin_user.save()

        tenant, _ = Tenant.objects.get_or_create(slug='e2e', defaults={'name': 'E2E Test'})
        token = set_current_tenant_id(tenant.id)
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT set_config('app.current_tenant_id', %s, false)",
                        [str(tenant.id)],
                    )

                from tenancy.models import TenantMembership

                TenantMembership.objects.get_or_create(
                    user=admin_user, tenant=tenant,
                    defaults={'role': 'operator', 'is_active': True},
                )
                TenantMembership.objects.filter(
                    user=admin_user, tenant=tenant,
                ).update(role='operator', is_active=True)

                company, _ = Company.objects.get_or_create(
                    tenant=tenant, name='E2E Company',
                    defaults={'is_active': True},
                )
                branch, _ = Branch.objects.get_or_create(
                    company=company, tenant=tenant, name='E2E Branch',
                )

                key_hash = hashlib.sha256(E2E_API_KEY.encode()).hexdigest()
                device, _ = Device.objects.get_or_create(
                    tenant=tenant, device_id='e2e-device-001',
                    defaults={
                        'name': 'E2E Test Device',
                        'key_hash': key_hash,
                        'branch': branch,
                        'platform': 'e2e',
                        'app_version': '0.1.0',
                        'status': 'active',
                        'registered_by': admin_user,
                    },
                )
                device.name = 'E2E Test Device'
                device.key_hash = key_hash
                device.branch = branch
                device.platform = 'e2e'
                device.app_version = '0.1.0'
                device.status = 'active'
                device.registered_by = admin_user
                device.save(update_fields=[
                    'name', 'key_hash', 'branch', 'platform', 'app_version',
                    'status', 'registered_by', 'updated_at',
                ])

                unit, _ = Unit.objects.get_or_create(
                    tenant=tenant, symbol='UN',
                    defaults={'name': 'Unidade', 'precision': 0},
                )

                cat, _ = Category.objects.get_or_create(
                    tenant=tenant, name='E2E Category',
                )

                product, _ = Product.objects.get_or_create(
                    tenant=tenant, sku='E2E-PROD-001',
                    defaults={
                        'name': 'Produto E2E',
                        'base_unit': unit,
                        'category': cat,
                        'ncm': '84713000',
                        'is_active': True,
                    },
                )
                product.name = 'Produto E2E'
                product.base_unit = unit
                product.category = cat
                product.ncm = '84713000'
                product.is_active = True
                product.save(update_fields=[
                    'name', 'base_unit', 'category', 'ncm', 'is_active', 'updated_at',
                ])

                ProductPrice.objects.update_or_create(
                    tenant=tenant, product=product,
                    valid_from='2026-01-01T00:00:00Z',
                    defaults={
                        'amount': 49.90,
                        'is_active': True,
                    },
                )

                location, _ = StockLocation.objects.get_or_create(
                    tenant=tenant, branch=branch, code='E2E-LOCAL',
                    defaults={
                        'name': 'Local E2E',
                        'location_type': 'general',
                        'is_primary': True,
                    },
                )

                with connection.cursor() as c:
                    c.execute(
                        "INSERT INTO fiscal_fiscalemitter "
                        "(id, tenant_id, branch_id, provider, cpf_cnpj, ie, "
                        "registered_at_provider, registration_source, created_at, updated_at) "
                        "SELECT %s, %s, %s, 'plugnotas', '00000000000000', "
                        "'111111111111', true, 'manual', NOW(), NOW() "
                        "WHERE NOT EXISTS ("
                        "SELECT 1 FROM fiscal_fiscalemitter "
                        "WHERE tenant_id=%s AND branch_id=%s AND provider='plugnotas'"
                        ")",
                        [
                            str(uuid.uuid4()),
                            str(tenant.id),
                            str(branch.id),
                            str(tenant.id),
                            str(branch.id),
                        ],
                    )

            self.stdout.write(self.style.SUCCESS(
                f'Dados E2E criados:\n'
                f'  Tenant: {tenant.slug}\n'
                f'  Branch: {branch.id}\n'
                f'  Device: {device.id} (API key: {E2E_API_KEY})\n'
                f'  Produto: {product.sku} (R$ 49,90)\n'
                f'  Local estoque: {location.code}'
            ))
        finally:
            reset_current_tenant_id(token)
