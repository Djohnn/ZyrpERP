# Sprint 19 — Gestão de PDV, Pessoas e Financeiro Web — Design

## Objetivo

Permitir que gestores supervisionem no frontend web as operações realizadas no PDV Electron, os cadastros de pessoas e seus efeitos financeiros, sem criar um segundo PDV.

## Limite explícito

O frontend web não realiza venda balcão, não imprime cupom e não oferece contingência offline. Essas responsabilidades permanecem exclusivas do PDV Electron.

## Gestão de vendas e caixas

- Consulta de vendas por período, filial, operador, dispositivo, cliente e estado fiscal.
- Detalhe de itens, pagamentos, estoque, documento fiscal e efeitos financeiros.
- Sessões de caixa, movimentos, abertura/fechamento e diferenças.
- Devolução, cancelamento e estorno com permissões, motivo e confirmação.
- Exportação limitada e auditável.

## Pessoas

- PF/PJ, papéis, documentos, contatos, endereços e consentimentos.
- Cliente identificado associado à venda e fornecedor associado à compra.
- Dados Restricted mascarados conforme papel e contexto.
- Desativação lógica sem remoção do histórico.

## Financeiro

- Contas a receber/pagar, liquidações e fluxo de caixa.
- Relatórios de vendas, caixa, estoque e financeiro.
- Filtros por período, conta, filial, status e origem.
- Navegação entre lançamento financeiro e operação de origem.

## Segurança e concorrência

- Ações corretivas exigem MFA quando definido pelo backend.
- Venda confirmada nunca é editada; correções criam fatos compensatórios.
- PII não aparece em URL, telemetria ou exportação não autorizada.
- Conflitos e operações já processadas retornam estado atual sem duplicação.

## Testes

- MSW para venda, caixa, devolução, estorno e liquidação.
- Playwright para localizar venda do PDV, inspecionar efeitos e executar correção autorizada.
- Testes cross-tenant e por papel para PII, vendas e financeiro.
- axe-core em relatórios, filtros e dialogs de confirmação.

## Fora do escopo

- Novo PDV web.
- Venda offline no navegador.
- Edição destrutiva de venda, caixa ou liquidação confirmados.

## Critérios de aceite

- Gestor acompanha integralmente uma venda originada no PDV.
- Sessões e diferenças de caixa são rastreáveis por operador/dispositivo.
- Correções geram eventos compensatórios auditados.
- Pessoas e financeiro permanecem tenant-scoped e protegidos.
- Nenhuma rota web executa o fluxo de venda balcão do Electron.
