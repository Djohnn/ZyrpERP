# Integration Contracts

## Regras
- Ports pertencem ao contexto consumidor.
- Adapters não vazam DTO do fornecedor.
- Timeout, idempotência, retry e circuit breaker são explícitos.
- Rejeição de negócio não recebe retry automático.
- Credenciais são referências a secrets, nunca payload de evento.

## FiscalProvider
Operações: cadastrar/validar emitente, emitir NF-e/NFC-e, consultar, cancelar, inutilizar, carta de correção, obter XML/DANFE e validar webhook.

## PaymentProvider
Operações futuras: criar cobrança, consultar, cancelar, estornar e validar webhook. Aprovação externa é distinta do registro no ERP.

## ObjectStorage
Operações: gravar, ler, criar URL temporária, verificar integridade e aplicar retenção. Chaves incluem tenant e classificação.

## NotificationGateway
Operações: enviar e-mail/notificação, consultar entrega e processar bounce. Mensagens são idempotentes por propósito e destinatário.
