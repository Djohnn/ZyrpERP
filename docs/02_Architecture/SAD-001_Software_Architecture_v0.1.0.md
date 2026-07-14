# SAD-001 — Software Architecture Document

| Campo | Valor |
|---|---|
| Código | SAD-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Arquitetura de Software |
| Aprovador | Architecture Owner |
| Última atualização | 2026-07-14 |
| Dependências | ADR-001 a ADR-006 |
| Documentos relacionados | DDD-001, SEC-001, API-001 |

## 1. Drivers
Isolamento SaaS, integridade financeira/fiscal, continuidade do PDV, auditabilidade, custo inicial e evolução modular.

## 2. Contexto
Atores usam Web React e PDV Electron. Ambos consomem API Django. Sistemas externos incluem provedor fiscal, pagamentos, e-mail e armazenamento S3 compatível.

## 3. Containers
- **Web React:** administração e operação online.
- **PDV Electron/React/SQLite:** venda online com contingência restrita.
- **Django/DRF:** monólito modular e autoridade de negócio.
- **Celery:** tarefas assíncronas, Outbox e integrações.
- **PostgreSQL/RLS:** persistência transacional multi-tenant.
- **Redis:** cache, locks curtos e broker; nunca fonte de verdade.
- **Object Storage:** XML, documentos e anexos com prefixo de tenant.

## 4. Módulos
Platform, Identity, Organizations, Catalog, Inventory, Purchasing, Sales, PDV, Cash Management, Financial, Fiscal, Analytics, Integrations e Audit.

Cada módulo contém `domain`, `application`, `infrastructure`, `interfaces` e `tests`. Interfaces chamam casos de uso; domínio não importa Django/DRF/Celery. Infrastructure implementa ports.

## 5. Fluxo HTTP
TLS → autenticação → resolução do tenant → autorização contextual → serializer de entrada → caso de uso transacional → resposta Problem Details ou DTO. `X-Correlation-ID` acompanha logs e eventos.

## 6. Persistência e RLS
Toda entidade de negócio possui `tenant_id`. Políticas RLS usam contexto transacional da conexão e deny-by-default. Jobs e comandos internos também estabelecem tenant. Consultas de suporte exigem fluxo auditado.

## 7. Assíncrono e Outbox
Caso de uso grava estado e Outbox na mesma transação. Celery publica, registra tentativas e mede idade. Consumidores usam event ID e idempotency store. Falhas definitivas seguem para dead-letter.

## 8. PDV
Dispositivo registrado recebe snapshots e deltas. Operações locais usam UUID, sequência, versão e journal persistente. Backend confirma lote idempotente. Funções administrativas exigem online.

## 9. Fiscal
Sales publica `SaleCompleted`; Fiscal cria solicitação e chama `FiscalProvider`. Máquina de estados preserva referência, XML, protocolo e rejeição. Webhooks são autenticados, deduplicados e auditados.

## 10. APIs
REST em `/api/v1`; OpenAPI é contrato. Dinheiro é string decimal com moeda. Datas usam ISO 8601. Concorrência usa version/ETag quando aplicável. Operações críticas exigem `Idempotency-Key`.

## 11. Segurança
MFA para funções sensíveis, secrets manager, criptografia de campos restritos, menor privilégio, CSP e proteção contra IDOR. Certificados e tokens não aparecem em logs nem no SQLite quando evitável.

## 12. Observabilidade
Logs JSON, correlation ID, métricas RED/USE, tracing OpenTelemetry, Sentry, dashboards de Outbox, fiscal e PDVs. Alertas distinguem falha técnica, rejeição de negócio e indisponibilidade externa.

## 13. Implantação
Docker em ambientes local, test, homologação, staging e produção. Web, worker e scheduler são processos separados da mesma base de código. Migrations são backward-compatible e release possui rollback documentado.

## 14. Evolução
Extração de serviço exige necessidade comprovada e preserva contracts/eventos. Analytics, Fiscal, Integrations e IA são candidatos futuros, não compromissos.

## 15. Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Arquitetura inicial. |

