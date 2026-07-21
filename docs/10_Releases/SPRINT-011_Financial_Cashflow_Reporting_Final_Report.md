# Sprint 11 — Financeiro, Fluxo de Caixa e Relatórios — Relatório Final

**Conclusão:** 2026-07-21  
**Branch:** `feat/on-demand-fiscal`

## Resumo

Sprint concluída com núcleo financeiro tenant-scoped, efeitos automáticos de vendas e compras,
liquidações parciais/totais, fluxo de caixa realizado/previsto e APIs gerenciais somente leitura.

## Entregas

- `FinancialAccount`, `Receivable`, `Payable`, `Settlement` e `CashflowEntry`.
- Constraints de valores positivos e idempotência por tenant.
- Imutabilidade de liquidações e lançamentos confirmados; correções exigem compensação.
- Venda em dinheiro/Pix gera realização imediata; cartão externo gera previsão.
- Recebimento de compra gera conta a pagar vinculada e idempotente.
- Liquidação parcial/total com bloqueio de baixa acima do saldo.
- Projeção por tenant, filial e período, separando realizado de previsto.

## APIs de relatórios

| Endpoint | Conteúdo |
|---|---|
| `GET /api/v1/reports/sales/` | total e quantidade de vendas |
| `GET /api/v1/reports/cash-closing/` | sessões e fechamento de caixa |
| `GET /api/v1/reports/inventory/` | quantidade, reservado, disponível e crítico |
| `GET /api/v1/reports/financial/` | contas a pagar e receber |
| `GET /api/v1/reports/cashflow/` | realizado, previsto e saldos |
| `GET /api/v1/reports/pending-operations/` | pendências fiscais e Outbox/offline |

Exportação financeira usa `export=csv` e aceita no máximo 1.000 linhas. `format` não é usado
porque é reservado pelo mecanismo de renderers do DRF.

## AI-readiness

- Read models permitidos e fontes proibidas registrados em
  `docs/03_Domain/AI_READINESS_READ_MODELS.md`.
- Dados financeiros e fiscais classificados em `docs/08_Security/DATA_CLASSIFICATION.md`.
- IA permanece somente leitura e sem ferramentas transacionais.

## Evidências

```text
Testes focados: 20 passed in 13.76s
Cobertura financial: 82.50% (mínimo 80%)
Ruff: All checks passed!
mypy: Success: no issues found in 201 source files
Django check: System check identified no issues (0 silenced).
Migrations: No changes detected
Suíte completa: 396 passed in 162.06s
Cobertura global configurada: 80.72%
```

## Fora do escopo

- DRE contábil completa, BI preditivo e integração bancária OFX/API.
- Conciliação automática de adquirentes.
- Qualquer copiloto executando ações transacionais.
