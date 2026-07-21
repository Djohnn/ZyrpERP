# Contrato de Provider de Pagamentos

## Responsabilidades

`sales` permanece responsável pela venda, `financial` pelos efeitos financeiros e `payments`
pela comunicação com providers, estados transacionais, webhooks e conciliação.

O contrato `PaymentProvider` separa:

- criação/autorização da intenção;
- captura;
- cancelamento;
- estorno;
- validação de assinatura de webhook.

## Pagamentos manuais e integrados

Pagamentos externos e manuais continuam registrados por `sales` sem configuração de provider.
Uma intenção em `payments` só é criada quando o fluxo integrado é solicitado explicitamente.

O provider fake oferece respostas determinísticas para testes e desenvolvimento. Ele não representa
homologação de adquirente real nem deve ser habilitado como meio real de captura.

## Idempotência e segurança

- Intenções são únicas por tenant e chave de idempotência.
- Referências de transação e IDs de webhook são únicos por tenant/provider.
- Assinaturas são verificadas antes de persistir o webhook.
- Segredos são classificados como `Restricted` e não aparecem em `__str__`, auditoria ou Outbox.
- Payloads de eventos contêm apenas IDs técnicos, provider e estado.

## Conciliação

Cada item compara `gross_amount - fee_amount` com `settled_amount`. Itens divergentes permanecem
em revisão manual e impedem a confirmação do lote. Lotes sem divergência geram lançamento
financeiro imutável da taxa, preservando a venda confirmada.
