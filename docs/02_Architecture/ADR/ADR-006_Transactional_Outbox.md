# ADR-006 — Transactional Outbox

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
Vendas, fiscal, sincronização e integrações precisam publicar eventos sem dual write entre banco e broker.

## Forças
Consistência, reprocessamento, observabilidade e evolução.

## Opções
1. Transactional Outbox. 2. Publicação direta após commit. 3. Transação distribuída.

## Decisão
Persistir evento Outbox na mesma transação do caso de uso; worker publica e marca entrega. Consumidores são idempotentes.

## Consequências positivas
- Estado e intenção de publicação são atômicos.
- Retentativa e auditoria claras.
- Integração externa desacoplada.

## Consequências negativas
- Entrega é pelo menos uma vez.
- Exige limpeza e monitoramento.
- Eventos não são instantâneos.

## Riscos
Backlog, publicação duplicada e payload incompatível.

## Mitigações
Idempotência, versionamento, métricas de idade, dead-letter e replay controlado.

## Critérios de revisão
Reavaliar transporte e CDC quando throughput justificar; preservar semântica do contrato.
