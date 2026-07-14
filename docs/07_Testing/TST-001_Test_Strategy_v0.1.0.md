# TST-001 — Test Strategy

| Campo | Valor |
|---|---|
| Código | TST-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | SRS-001, SAD-001, SEC-001 |
| Última atualização | 2026-07-14 |

## Estratégia
Testar domínio e casos de uso rapidamente; integração com PostgreSQL real para transação e RLS; contratos nas fronteiras; E2E apenas para jornadas críticas; caos para offline, fiscal e restauração.

## Camadas
- Unidade: invariantes, dinheiro, conversões e estados.
- Aplicação: autorização, transação, idempotência e Outbox.
- Integração: ORM, RLS, Celery, cache, storage e providers fake.
- API/contrato: OpenAPI, Problem Details e compatibilidade.
- E2E: onboarding, compra, venda, caixa, fiscal e devolução.
- Caos: queda de rede, reinício do PDV, replay, indisponibilidade fiscal e restauração.

## Suítes obrigatórias
RLS e IDOR com dois tenants; idempotência; offline; fiscal; dinheiro; estoque; caixa; webhooks; migration PostgreSQL/SQLite; backup e restauração; performance e segurança.

## Gates
Pull request exige unidade, lint e contrato. Staging exige integração/E2E. Produção exige segurança, restore evidenciado, smoke test, rollback e riscos aceitos.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Estratégia inicial. |

