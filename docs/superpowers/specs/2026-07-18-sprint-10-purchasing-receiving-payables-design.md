# Sprint 10 — Compras, Recebimento e Contas a Pagar Design

## Objetivo

Implementar o fluxo de compra essencial: fornecedor, pedido de compra, recebimento parcial/total, entrada de estoque e obrigação financeira a pagar.

## Escopo

Esta sprint adiciona o primeiro backoffice de reposição. Ela não tenta resolver negociação avançada, cotação com múltiplos fornecedores ou fiscal de entrada completo; foca no fluxo mínimo confiável.

## Arquitetura

Criar o app `purchasing` e integrar com:

- `catalog` para produtos, unidades e conversões;
- `inventory` para entrada de estoque;
- `financial` ou módulo inicial de payables para obrigação a pagar;
- `audit` e `outbox` para rastreabilidade.

Fluxo:

1. cadastrar fornecedor mínimo;
2. criar pedido de compra com itens;
3. aprovar/enviar pedido;
4. receber parcial ou total;
5. gerar `StockOperation` de entrada;
6. criar obrigação financeira vinculada;
7. reconciliar divergência entre pedido, recebido e valor a pagar.

## Regras de negócio

- Pedido aprovado não é editado sem nova versão/evento.
- Recebimento parcial é permitido.
- Não receber quantidade acima do saldo pendente sem permissão explícita.
- Entrada de estoque é idempotente por recebimento.
- Obrigação financeira nasce do recebimento confirmado.
- Fornecedor pertence ao tenant.
- Custo unitário usa `Decimal`, nunca `float`.

## Modelos previstos

- `Supplier`
- `PurchaseOrder`
- `PurchaseOrderItem`
- `PurchaseReceipt`
- `PurchaseReceiptItem`
- `Payable`

## APIs previstas

- CRUD de fornecedores.
- Criar/listar/aprovar pedido de compra.
- Registrar recebimento.
- Consultar saldo pendente por pedido.
- Listar contas a pagar geradas.

## Fora do escopo

- Cotação/RFQ com múltiplos fornecedores.
- Fiscal de entrada completo.
- Custo médio contábil avançado.
- Integração bancária.
- Automação de pedido sugerido por IA.

## Critérios de aceite

- Pedido aprovado gera histórico imutável.
- Recebimento parcial aumenta estoque exatamente na quantidade recebida.
- Reenvio idempotente não duplica estoque nem conta a pagar.
- Conta a pagar reflete valor recebido.
- Testes bloqueiam relação cross-tenant.
