# Sprint 11 — Financeiro, Fluxo de Caixa e Relatórios Operacionais Design

## Objetivo

Consolidar financeiro operacional e relatórios gerenciais básicos: contas a pagar, contas a receber, liquidações, fluxo de caixa e consultas de vendas/estoque/caixa/fiscal.

## Escopo

A Sprint 11 cria a visão financeira mínima para o gestor acompanhar dinheiro, obrigações e resultado operacional por tenant, empresa e filial.

## Arquitetura

Criar ou consolidar app `financial` com lançamentos imutáveis e projeções de leitura. Eventos de `sales`, `purchasing`, `cash` e `fiscal` alimentam relatórios e saldos reconciliáveis.

Fluxo:

1. vendas geram recebíveis/liquidações conforme forma de pagamento;
2. compras geram contas a pagar;
3. liquidações baixam obrigações;
4. relatórios consultam projeções ou queries otimizadas;
5. divergências ficam visíveis e auditáveis.

## Regras de negócio

- Lançamento financeiro confirmado não é editado; correção é lançamento compensatório.
- Dinheiro, Pix, cartão externo e cartão integrado têm datas de disponibilidade distintas.
- Fluxo de caixa separa realizado de previsto.
- Relatórios respeitam tenant, empresa, filial e período.
- Dados financeiros são `Restricted` ou `Confidential` conforme classificação.
- Exportação não inclui segredo, token, certificado ou payload fiscal sensível.

## Modelos previstos

- `FinancialAccount`
- `Receivable`
- `Payable`
- `Settlement`
- `CashflowEntry`
- `ReportSnapshot`

## Relatórios previstos

- Vendas por período, filial, produto e forma de pagamento.
- Fechamento de caixa consolidado.
- Estoque atual e produtos críticos.
- Contas a pagar e receber.
- Fluxo de caixa realizado e previsto.
- Pendências fiscais e offline.

## Fora do escopo

- BI preditivo.
- DRE contábil completa.
- Integração bancária OFX/API.
- Conciliação automática de adquirentes.
- Copiloto de IA executando ações.

## Critérios de aceite

- Relatórios não vazam dados cross-tenant.
- Lançamentos são imutáveis e auditados.
- Fluxo de caixa bate com vendas, compras e liquidações de teste.
- Exportações possuem filtros e limites.
- Base fica preparada para IA/RAG somente leitura no futuro.
