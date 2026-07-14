from django.db import migrations


CREATE_TRIGGER = """
CREATE OR REPLACE FUNCTION tenancy_enforce_branch_company_tenant()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM tenancy_company company
        WHERE company.id = NEW.company_id
          AND company.tenant_id = NEW.tenant_id
    ) THEN
        RAISE EXCEPTION 'branch tenant must match company tenant'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tenancy_branch_company_tenant_guard ON tenancy_branch;
CREATE TRIGGER tenancy_branch_company_tenant_guard
BEFORE INSERT OR UPDATE OF tenant_id, company_id ON tenancy_branch
FOR EACH ROW EXECUTE FUNCTION tenancy_enforce_branch_company_tenant();
"""

DROP_TRIGGER = """
DROP TRIGGER IF EXISTS tenancy_branch_company_tenant_guard ON tenancy_branch;
DROP FUNCTION IF EXISTS tenancy_enforce_branch_company_tenant();
"""


class Migration(migrations.Migration):
    dependencies = [('tenancy', '0002_rls_policies')]

    operations = [migrations.RunSQL(CREATE_TRIGGER, DROP_TRIGGER)]
