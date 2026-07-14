#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_APP_USER:=zyrp_app}"
: "${POSTGRES_APP_PASSWORD:=zyrp_app_dev}"
: "${POSTGRES_TEST_USER:=zyrp_test}"
: "${POSTGRES_TEST_PASSWORD:=zyrp_test_dev}"

psql_host_args=()
if [[ -n "${POSTGRES_HOST:-}" ]]; then
  psql_host_args+=(--host "${POSTGRES_HOST}" --port "${POSTGRES_PORT:-5432}")
fi

psql --set ON_ERROR_STOP=1 \
  "${psql_host_args[@]}" \
  --username "${POSTGRES_USER}" \
  --dbname "${POSTGRES_DB}" \
  --set app_user="${POSTGRES_APP_USER}" \
  --set app_password="${POSTGRES_APP_PASSWORD}" \
  --set test_user="${POSTGRES_TEST_USER}" \
  --set test_password="${POSTGRES_TEST_PASSWORD}" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS NOCREATEDB', :'app_user', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_user') \gexec

SELECT format('ALTER ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS NOCREATEDB', :'app_user', :'app_password') \gexec

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS CREATEDB', :'test_user', :'test_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'test_user') \gexec

SELECT format('ALTER ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS CREATEDB', :'test_user', :'test_password') \gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), :'app_user') \gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), :'test_user') \gexec
SELECT format('GRANT USAGE ON SCHEMA public TO %I', :'app_user') \gexec
SELECT format('GRANT USAGE, CREATE ON SCHEMA public TO %I', :'test_user') \gexec
SELECT format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO %I', :'app_user') \gexec
SELECT format('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO %I', :'app_user') \gexec
SELECT format('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I', :'app_user') \gexec
SELECT format('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO %I', :'app_user') \gexec
SQL
