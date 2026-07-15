from django.db import migrations

CATALOG_TENANT_SCOPED_TABLES = [
    'catalog_unit',
    'catalog_category',
    'catalog_product',
    'catalog_productunit',
    'catalog_productcode',
    'catalog_productprice',
    'catalog_branchprice',
]


def enable_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in CATALOG_TENANT_SCOPED_TABLES:
            cursor.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
            cursor.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY;')
            cursor.execute(f"""
                CREATE POLICY tenant_isolation_policy ON {table}
                    FOR ALL
                    USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE))
                    WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', TRUE));
            """)


def disable_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in CATALOG_TENANT_SCOPED_TABLES:
            cursor.execute(f'DROP POLICY IF EXISTS tenant_isolation_policy ON {table};')
            cursor.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY OFF;')
            cursor.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0003_branchprice_productprice'),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]