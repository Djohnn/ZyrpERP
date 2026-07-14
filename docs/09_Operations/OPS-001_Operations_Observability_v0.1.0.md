# OPS-001 — Operations and Observability

| Campo | Valor |
|---|---|
| Código | OPS-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | SAD-001, TST-001 |
| Última atualização | 2026-07-14 |

## Telemetria
Logs JSON sem segredos, métricas RED/USE, tracing OpenTelemetry, Sentry e correlation ID ponta a ponta.

## Sinais críticos
Latência/erro/saturação de API; idade e falha da Outbox; filas Celery; conexões DB; rejeições e indisponibilidade fiscal; PDVs offline; operações não sincronizadas; jobs de backup.

## SLOs
Valores numéricos serão aprovados antes do piloto usando baseline de carga. Todo SLO possui indicador, janela, orçamento de erro, owner e ação quando violado.

## Backup e recuperação
Backup criptografado, retenção por classe, cópia isolada, teste periódico de restore, RPO/RTO aprovados antes da produção e evidência auditável.

## Runbooks
Cobrir indisponibilidade API, fila parada, Outbox atrasada, fiscal indisponível, certificado vencido, PDV sem sincronizar, banco degradado e restore.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Operação inicial. |

