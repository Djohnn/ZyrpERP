# REL-001 — Release Strategy

| Campo | Valor |
|---|---|
| Código | REL-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | PG-001, TST-001, OPS-001 |
| Última atualização | 2026-07-14 |

## Ambientes
Local → Test → Homologação → Staging → Produção. Fiscal possui credenciais e endpoints separados.

## Processo
Build imutável, checks, migration backward-compatible, deploy canary do backend, smoke test, expansão gradual e observação. Feature flags separam deploy de release.

## PDV
Canal de atualização gradual, versão mínima suportada, migração SQLite testada, protocolo compatível e rollback de aplicação sem perder journal.

## Rollback
Código reverte para imagem anterior; banco usa estratégia expand/contract; dados compensam em vez de apagar fatos. Critérios de abort estão definidos antes do deploy.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Estratégia inicial. |
