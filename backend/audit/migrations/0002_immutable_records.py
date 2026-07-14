from django.db import migrations


CREATE_GUARD = """
CREATE OR REPLACE FUNCTION audit_prevent_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit records are immutable' USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS audit_record_immutable_guard ON audit_auditrecord;
CREATE TRIGGER audit_record_immutable_guard
BEFORE UPDATE OR DELETE ON audit_auditrecord
FOR EACH ROW EXECUTE FUNCTION audit_prevent_mutation();
"""

DROP_GUARD = """
DROP TRIGGER IF EXISTS audit_record_immutable_guard ON audit_auditrecord;
DROP FUNCTION IF EXISTS audit_prevent_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [('audit', '0001_initial')]

    operations = [migrations.RunSQL(CREATE_GUARD, DROP_GUARD)]
