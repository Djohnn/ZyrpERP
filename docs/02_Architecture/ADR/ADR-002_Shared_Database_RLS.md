# ADR-002 — Banco compartilhado com RLS

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
O SaaS precisa isolar tenants com custo e complexidade adequados ao MVP.

## Forças
Segurança, custo, migrations, operação, analytics e crescimento.

## Opções
1. Banco compartilhado com `tenant_id` e RLS. 2. Schema por tenant. 3. Banco por tenant.

## Decisão
Usar PostgreSQL compartilhado, `tenant_id` obrigatório e RLS como defesa adicional. Aplicação, cache, arquivos, tarefas e eventos também aplicam escopo.

## Consequências positivas
- Operação e migrations centralizadas.
- Uso eficiente de recursos.
- Consultas administrativas controladas.

## Consequências negativas
- Uma consulta incorreta pode ter alto impacto sem defesas.
- RLS aumenta complexidade de conexão e testes.
- Grandes tenants compartilham recursos.

## Riscos
IDOR, bypass de RLS, cache cruzado e tarefas sem contexto.

## Mitigações
Contexto explícito, deny-by-default, testes negativos, chaves de cache prefixadas e auditoria.

## Critérios de revisão
Reavaliar isolamento físico para requisitos regulatórios, residência de dados ou tenants de escala excepcional.

