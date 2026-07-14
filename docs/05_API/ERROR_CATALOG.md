# API Error Catalog

| Família | Exemplo | HTTP | Retry |
|---|---|---:|---|
| AUTH | `AUTH_INVALID_CREDENTIALS` | 401 | Não |
| TENANT | `TENANT_CONTEXT_DENIED` | 404 | Não |
| VALIDATION | `VALIDATION_FAILED` | 422 | Após correção |
| CONFLICT | `CONFLICT_VERSION_MISMATCH` | 409 | Recarregar |
| INVENTORY | `INVENTORY_INSUFFICIENT` | 409 | Regra configurável |
| CASH | `CASH_SESSION_CLOSED` | 409 | Não |
| FISCAL | `FISCAL_DOCUMENT_REJECTED` | 422 | Após correção |
| SYNC | `SYNC_SEQUENCE_GAP` | 409 | Reconciliar |
| INTERNAL | `INTERNAL_UNEXPECTED` | 500 | Backoff limitado |

Recursos de outro tenant retornam resposta indistinguível de recurso inexistente. Rejeição de negócio não recebe retry automático.

