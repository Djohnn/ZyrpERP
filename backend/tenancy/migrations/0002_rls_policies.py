from django.db import migrations

TENANT_SCOPED_TABLES = [
    'tenancy_company',
    'tenancy_branch',
]


def enable_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE tenancy_company ENABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE tenancy_company FORCE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE tenancy_branch ENABLE ROW LEVEL SECURITY;")
        cursor.execute("ALTER TABLE tenancy_branch FORCE ROW LEVEL SECURITY;")

        # Policy per tabela: tenant_id deve bater com o contexto da sessão
        for table in TENANT_SCOPED_TABLES:
            cursor.execute(f"""
                CREATE POLICY tenant_isolation_policy ON {table}
                    FOR ALL
                    USING (tenant_id::text = current_setting('app.current_tenant_id', TRUE))
                    WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', TRUE));
            """)


def disable_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in TENANT_SCOPED_TABLES:
            cursor.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table};")
            cursor.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY OFF;")
            cursor.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")


class Migration(migrations.Migration):
    dependencies = [
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]
