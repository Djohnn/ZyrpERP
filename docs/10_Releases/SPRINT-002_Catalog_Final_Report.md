# Sprint 2 — Catálogo e Cadastros-base — Relatório Final

Data de fechamento: 2026-07-16

## Resultado

A Sprint 2 entrega o módulo `catalog` com categorias, unidades, produtos, unidades comerciais, códigos, preços por vigência, sobrescrita por filial, isolamento por tenant, permissões por capability e eventos via Outbox.

Após revisão de hardening em 2026-07-16, foram corrigidos pontos que impediam considerar o catálogo como base segura para estoque, vendas e PDV:

- busca `?search=` em endpoints de catálogo agora usa o model correto do queryset;
- serializers de catálogo executam `full_clean()` antes de salvar, preservando validações de domínio expostas nos models;
- rotas aninhadas de unidades, códigos e preços forçam o produto da URL, evitando divergência entre URL e payload;
- testes de regressão foram adicionados para busca, FKs cross-tenant, produto divergente em rota aninhada e sobreposição de preço;
- OpenAPI foi complementado com endpoints principais da Sprint 2;
- catálogo de eventos foi complementado com eventos de catálogo versionados.

## Evidências desta rodada

Comandos executados:

```text
C:\ERP\.venv\Scripts\python.exe manage.py check
Resultado: System check identified no issues (0 silenced).
```

```text
C:\ERP\.venv\Scripts\python.exe -m ruff check catalog tests/test_catalog_api_hardening.py
Resultado: All checks passed!
```

```text
C:\ERP\.venv\Scripts\python.exe -m pytest tests/test_catalog_api_hardening.py --collect-only -vv -o addopts=''
Resultado: 5 tests collected.
```

## Revalidação no pre-flight da Sprint 4

Em 2026-07-17, o setup de testes com banco PostgreSQL pré-provisionado foi estabilizado para reiniciar dados de aplicação no início da sessão e evitar inconsistências de `contenttypes`/`auth_permissions` em testes transacionais.

Comandos reexecutados com sucesso:

```text
C:\ERP\.venv\Scripts\python.exe -m pytest tests/test_catalog_rls.py -q -o addopts=''
Resultado: 9 passed.
```

```text
C:\ERP\.venv\Scripts\python.exe -m pytest -q
Resultado: 192 passed, cobertura total 80.19%.
```

## Riscos e decisões

- A Sprint 2 não usa `ExclusionConstraint` para impedir sobreposição de preços porque isso depende de extensão PostgreSQL adicional (`btree_gist`) não padronizada para o ambiente de teste atual.
- A regra de não sobreposição fica validada em `model.clean()` e agora também é acionada pelo caminho da API via serializers.
- O isolamento multi-tenant continua dependendo de defesa em camadas: tenant manager, RLS, permissões, sessão MFA e validação de FKs no domínio.

## Arquivos principais

- `backend/catalog/models.py`
- `backend/catalog/serializers.py`
- `backend/catalog/views.py`
- `backend/catalog/urls.py`
- `backend/tests/test_catalog_api_hardening.py`
- `docs/05_API/openapi.yaml`
- `docs/03_Domain/DOMAIN_EVENT_CATALOG.md`

## Status

Status técnico: hardening aplicado, validação estática concluída e regressão com banco revalidada no pre-flight da Sprint 4.

Status de testes com banco: aprovado localmente com PostgreSQL real. CI remota deve ser validada no PR/merge.
