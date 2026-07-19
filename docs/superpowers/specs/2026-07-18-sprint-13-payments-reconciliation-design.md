# Sprint 13 — Pagamentos Integrados e Conciliação Design

## Objetivo

Evoluir o registro manual de pagamentos para integração controlada com provedores de pagamento e conciliação operacional de Pix, cartão externo/integrado e liquidações financeiras.

## Escopo

A Sprint 13 cria contratos e infraestrutura para pagamentos integrados sem obrigar todas as pequenas empresas a usar maquineta integrada. O sistema continuará aceitando pagamento externo/manual, mas terá adaptadores para provedores configurados por tenant.

## Arquitetura

Criar o app `payments` como camada de integração e conciliação. `sales` continua dono da venda; `financial` continua dono dos efeitos financeiros; `payments` registra intenção, autorização, captura, webhook e reconciliação.

Fluxo integrado:

1. venda solicita pagamento integrado;
2. `PaymentProvider` cria intenção/cobrança;
3. operador confirma/captura ou webhook atualiza estado;
4. evento financeiro é conciliado;
5. divergência fica visível para correção manual.

## Modelos previstos

- `PaymentProviderConfig`
- `PaymentIntent`
- `PaymentTransaction`
- `PaymentWebhookEvent`
- `PaymentReconciliationBatch`
- `PaymentReconciliationItem`

## Regras de negócio

- Pagamento externo/manual continua permitido.
- Webhook é idempotente e valida assinatura quando provider suportar.
- Autorização/captura/estorno são estados separados.
- Valor liquidado pode divergir do valor bruto por taxas.
- Conciliação não altera venda confirmada; cria ajustes financeiros.
- Segredos de provider são `Restricted` e nunca entram em log.

## APIs previstas

- `POST /api/v1/payments/intents/`
- `POST /api/v1/payments/webhooks/{provider}/`
- `GET /api/v1/payments/transactions/`
- `POST /api/v1/payments/reconciliation-batches/`
- `POST /api/v1/payments/reconciliation-batches/{id}/confirm/`

## Fora do escopo

- Certificação TEF nacional completa.
- Homologação de cada adquirente real.
- Split de pagamento.
- Marketplace de pagamentos.
- Crédito próprio.

## Critérios de aceite

- Pagamento manual permanece funcionando.
- Provider fake cobre intenção, captura, falha e webhook.
- Webhook duplicado não duplica transação.
- Conciliação gera diferença visível quando valor líquido diverge.
- Dados secretos do provider não aparecem em auditoria, log ou Outbox.
