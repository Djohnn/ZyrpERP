# Domain Event Catalog

Todo evento contém `event_id`, `event_type`, `event_version`, `occurred_at`, `tenant_id`, `correlation_id`, `aggregate_id` e payload sem segredos.

| Evento | Versão | Produtor | Consumidores | Payload mínimo |
|---|---:|---|---|---|
| `SaleCompleted` | 1 | Sales | Inventory, Cash, Financial, Fiscal, Analytics | sale, branch, totals, payment summary |
| `StockMovementRecorded` | 1 | Inventory | Analytics, Purchasing | movement, product, quantity, reason |
| `PurchaseReceived` | 1 | Purchasing | Inventory, Financial, Analytics | receipt, supplier, items, totals |
| `CashSessionClosed` | 1 | Cash | Financial, Analytics, Audit | session, expected, declared, difference |
| `FiscalDocumentRequested` | 1 | Fiscal | Integrations, Audit | document, sale, type, provider account |
| `FiscalDocumentAuthorized` | 1 | Fiscal | Sales, PDV, Analytics, Audit | document, access key, protocol, artifact refs |
| `FiscalDocumentRejected` | 1 | Fiscal | Sales, PDV, Audit | document, code, reason, correctable |
| `PDVOperationSynchronized` | 1 | PDV | Sales, Cash, Audit | device, local operation, server reference |
| `catalog.product.created` | 1 | Catalog | Inventory, PDV, Analytics, Audit | product id, sku, active flag, version |
| `catalog.product.updated` | 1 | Catalog | Inventory, PDV, Analytics, Audit | product id, changed fields, version |
| `catalog.product.deactivated` | 1 | Catalog | Inventory, PDV, Analytics, Audit | product id, deactivated at, version |
| `catalog.productcode.created` | 1 | Catalog | PDV, Integrations, Analytics, Audit | code id, product id, type, value |
| `catalog.productunit.created` | 1 | Catalog | Inventory, PDV, Analytics, Audit | product unit id, product id, unit id, factor |
| `catalog.price.changed` | 1 | Catalog | PDV, Sales, Analytics, Audit | price id, product id, branch id, amount, validity |

Consumidores deduplicam por `event_id`. Mudança incompatível cria nova versão; eventos publicados não são reescritos.

