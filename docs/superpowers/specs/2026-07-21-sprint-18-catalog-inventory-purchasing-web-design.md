# Sprint 18 — Catálogo, Estoque e Compras Web — Design

## Objetivo

Disponibilizar no painel web a gestão integrada de produtos, preços, estoque, fornecedores, pedidos de compra e recebimentos.

## Escopo

Construir jornadas verticais sobre APIs existentes, complementando apenas contratos indispensáveis para paginação, filtros, concorrência e feedback transacional.

## Módulos

### Catálogo

- Categorias, unidades, produtos, códigos e conversões.
- Preços vigentes e futuros por filial.
- Busca por SKU, código de barras e nome.
- Alertas de inconsistência fiscal/cadastral.

### Estoque

- Saldos por filial e local.
- Movimentações, lotes, validade e rastreabilidade.
- Recebimento, transferência, ajuste e inventário.
- Alertas de estoque crítico e divergência.

### Compras

- Fornecedores vinculados a pessoas.
- Pedido em rascunho, aprovação e recebimento parcial/total.
- Cancelamentos, devoluções e recorrência.
- Contas a pagar e reconciliação fiscal associadas.

## Regras de interação

- Escritas enviam idempotency key quando o endpoint exigir.
- Conflitos `409` preservam o formulário e oferecem recarregamento seguro.
- Valores monetários e quantidades usam representação decimal sem `float`.
- Ações irreversíveis exigem confirmação e exibem efeito previsto.

## Testes

- Unitários para formatação, decimal, filtros e adapters de API.
- Integração com MSW para todos os estados de pedido/recebimento.
- Playwright para produto → estoque → compra → recebimento.
- Testes de acessibilidade em tabelas densas e formulários dinâmicos.

## Fora do escopo

- Produção/MRP.
- Integração automática com marketplace de fornecedores.
- Operação offline no navegador.

## Critérios de aceite

- Usuário autorizado completa cadastro e precificação de produto.
- Estoque pode ser consultado e movimentado com rastreabilidade.
- Pedido de compra percorre aprovação e recebimento sem duplicidade.
- Recebimento atualiza estoque, fiscal e financeiro de forma visível.
- Dados de outra filial/tenant não aparecem em filtros ou seletores.
