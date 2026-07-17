from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from tenancy.context import reset_current_tenant_id, set_current_tenant_id
from tenancy.models import Branch, Company, Tenant, TenantMembership

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """Use the pre-provisioned PostgreSQL test database.

    The project uses separate runtime and migration owners. Letting
    pytest-django create/drop the database locally goes through Django's
    administrative _nodb connection path and hangs in this Windows/Postgres
    setup. Migrations are applied explicitly with config.settings.migration.
    """
    import psycopg
    from decouple import Config, RepositoryEnv, config
    from django.conf import settings
    from django.core.management import call_command
    from psycopg import sql

    test_name = settings.DATABASES['default'].get('TEST', {}).get('NAME')
    if test_name:
        settings.DATABASES['default']['NAME'] = test_name
    database = settings.DATABASES['default']
    runtime_user = database['USER']
    env_path = Path(__file__).resolve().parents[2] / '.env'
    env_config = Config(RepositoryEnv(str(env_path))) if env_path.exists() else config
    owner_user = env_config('POSTGRES_USER', default='zyrp')
    owner_password = env_config('POSTGRES_PASSWORD', default='zyrp')
    conn = psycopg.connect(
        dbname=database['NAME'],
        user=owner_user,
        password=owner_password,
        host=database['HOST'],
        port=database['PORT'],
        connect_timeout=5,
    )
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename <> 'django_migrations'
            ORDER BY tablename
            """
        )
        tables = [row[0] for row in cursor.fetchall()]
        if tables:
            cursor.execute(
                sql.SQL('TRUNCATE TABLE {} RESTART IDENTITY CASCADE').format(
                    sql.SQL(', ').join(
                        sql.Identifier('public', table) for table in tables
                    )
                )
            )
        cursor.execute(sql.SQL('GRANT USAGE ON SCHEMA public TO {}').format(
            sql.Identifier(runtime_user),
        ))
        cursor.execute(sql.SQL(
            'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}'
        ).format(sql.Identifier(runtime_user)))
        cursor.execute(sql.SQL(
            'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {}'
        ).format(sql.Identifier(runtime_user)))
    conn.commit()
    conn.close()
    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0, interactive=False)


def _run_in_tenant(tenant, callback):
    token = set_current_tenant_id(tenant.id)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET app.current_tenant_id = %s', [str(tenant.id)])
        return callback()
    finally:
        reset_current_tenant_id(token)


@pytest.fixture
def tenant_alpha():
    t, _ = Tenant.objects.get_or_create(
        slug='test-alpha', defaults={'name': 'Test Alpha'},
    )
    return t


@pytest.fixture
def tenant_beta():
    t, _ = Tenant.objects.get_or_create(
        slug='test-beta', defaults={'name': 'Test Beta'},
    )
    return t


@pytest.fixture
def user_alpha(tenant_alpha):
    u, _ = User.objects.get_or_create(email='user-alpha@test.local')
    u.set_password('pass123')
    u.save()
    TenantMembership.objects.get_or_create(
        user=u, tenant=tenant_alpha, defaults={'role': 'admin'},
    )
    return u


@pytest.fixture
def user_beta(tenant_beta):
    u, _ = User.objects.get_or_create(email='user-beta@test.local')
    u.set_password('pass123')
    u.save()
    TenantMembership.objects.get_or_create(
        user=u, tenant=tenant_beta, defaults={'role': 'admin'},
    )
    return u


@pytest.fixture
def company_alpha(tenant_alpha):
    return _run_in_tenant(
        tenant_alpha,
        lambda: Company.objects.get_or_create(
            tenant=tenant_alpha, name='Alpha Company',
        )[0],
    )


@pytest.fixture
def company_beta(tenant_beta):
    return _run_in_tenant(
        tenant_beta,
        lambda: Company.objects.get_or_create(
            tenant=tenant_beta, name='Beta Company',
        )[0],
    )


@pytest.fixture
def branch_alpha(company_alpha, tenant_alpha):
    return _run_in_tenant(
        tenant_alpha,
        lambda: Branch.objects.get_or_create(
            company=company_alpha, tenant=tenant_alpha, name='Alpha Branch',
        )[0],
    )


@pytest.fixture
def branch_beta(company_beta, tenant_beta):
    return _run_in_tenant(
        tenant_beta,
        lambda: Branch.objects.get_or_create(
            company=company_beta, tenant=tenant_beta, name='Beta Branch',
        )[0],
    )


# ==================== INVENTORY FIXTURES ====================

@pytest.fixture
def inv_tenant():
    return Tenant.objects.get_or_create(name='Inv', slug='inv-test')[0]


@pytest.fixture
def inv_unit(inv_tenant):
    from catalog.models import Unit
    return _run_in_tenant(
        inv_tenant,
        lambda: Unit.all_objects.get_or_create(
            tenant=inv_tenant,
            symbol='kg',
            defaults={'name': 'Quilograma', 'precision': 3},
        )[0],
    )


@pytest.fixture
def inv_unit_un(inv_tenant):
    from catalog.models import Unit
    return _run_in_tenant(
        inv_tenant,
        lambda: Unit.all_objects.get_or_create(
            tenant=inv_tenant,
            symbol='un',
            defaults={'name': 'Un', 'precision': 0},
        )[0],
    )


@pytest.fixture
def inv_product(inv_tenant, inv_unit):
    from catalog.models import Product
    return _run_in_tenant(
        inv_tenant,
        lambda: Product.all_objects.get_or_create(
            tenant=inv_tenant,
            sku='INV-001',
            defaults={
                'name': 'Produto Inv',
                'base_unit': inv_unit,
                'requires_lot': True,
                'requires_expiry': True,
            },
        )[0],
    )


@pytest.fixture
def inv_company(inv_tenant):
    return _run_in_tenant(
        inv_tenant,
        lambda: Company.objects.get_or_create(tenant=inv_tenant, name='InvCo')[0],
    )


@pytest.fixture
def inv_branch(inv_company, inv_tenant):
    return _run_in_tenant(
        inv_tenant,
        lambda: Branch.objects.get_or_create(
            company=inv_company,
            tenant=inv_tenant,
            name='InvBranch',
        )[0],
    )
