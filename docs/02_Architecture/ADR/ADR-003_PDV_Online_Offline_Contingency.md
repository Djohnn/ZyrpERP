# ADR-003 — PDV online com contingência offline

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
O caixa não pode parar em falhas breves, mas sincronizar todo o ERP amplia conflitos e risco fiscal.

## Forças
Continuidade, integridade, segurança local e simplicidade operacional.

## Opções
1. Online com contingência restrita. 2. Offline-first completo. 3. Somente online.

## Decisão
Electron + React + SQLite, online por padrão. Offline limita-se a catálogo em cache, sessão de caixa, venda, pagamento confirmado e contingência fiscal permitida.

## Consequências positivas
- Menor superfície de conflito.
- Continuidade do fluxo essencial.
- Backend permanece autoridade consolidada.

## Consequências negativas
- Funções administrativas ficam indisponíveis offline.
- Estoque local pode ficar desatualizado.
- Sincronização ainda exige engenharia rigorosa.

## Riscos
Venda duplicada, perda local, conflito de preço e atraso fiscal.

## Mitigações
UUID, idempotência, WAL, journal append-only, versões e painel de pendências.

## Critérios de revisão
Expandir escopo offline somente com evidência de demanda e testes de caos aprovados.

