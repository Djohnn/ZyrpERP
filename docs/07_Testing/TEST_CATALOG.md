# Test Catalog

| ID | Área | Objetivo | Nível |
|---|---|---|---|
| TEST-TENANT-001 | RLS | Bloquear leitura cross-tenant | Integration |
| TEST-TENANT-002 | IDOR | Ocultar recurso fora do contexto | API |
| TEST-SALE-001 | Sales | Retry não duplica venda | Application |
| TEST-STOCK-001 | Inventory | Saldo deriva de movimentos | Domain |
| TEST-CASH-001 | Cash | Fechamento preserva diferença | E2E |
| TEST-FISCAL-001 | Fiscal | Webhook duplicado é idempotente | Contract |
| TEST-SYNC-001 | PDV | Lote repetido não duplica operação | Integration |
| TEST-CHAOS-001 | PDV | Reinício recupera journal | Chaos |
| TEST-RESTORE-001 | Operations | Backup restaura serviço íntegro | Recovery |

