# DDD-001 — Domain Design

| Campo | Valor |
|---|---|
| Código | DDD-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Domain Architecture |
| Aprovador | Architecture Owner |
| Última atualização | 2026-07-14 |
| Dependências | PB-001, SAD-001 |
| Documentos relacionados | DOMAIN_EVENT_CATALOG, INTEGRATION_CONTRACTS |

## 1. Abordagem
DDD leve: linguagem ubíqua, bounded contexts, agregados, invariantes, application services e eventos. Não criar abstração sem regra real.

## 2. Contextos
| Contexto | Responsabilidade | Agregados centrais | Dependências permitidas |
|---|---|---|---|
| Platform | tenant, plano e feature flags | Tenant | nenhuma de negócio |
| Identity | identidade e acesso | User, Membership, Role | Platform, Organizations |
| Organizations | empresas e filiais | Company, Branch | Platform |
| Catalog | identidade comercial | Product, Category, Unit | Organizations |
| Inventory | custódia e saldo | StockMovement, InventoryCount | Catalog, Organizations |
| Purchasing | aquisição | PurchaseOrder, Receipt | Catalog, Inventory |
| Sales | venda e devolução | Sale, Return | Catalog, Inventory |
| PDV | dispositivo e sincronização | Device, SyncBatch | Sales, Cash |
| Cash | caixa físico | CashSession, CashMovement | Sales, Organizations |
| Financial | obrigações e liquidação | Receivable, Payable, Settlement | Sales, Purchasing |
| Fiscal | documentos fiscais | FiscalDocument | Sales, Organizations |
| Analytics | projeções de leitura | ReportSnapshot | eventos dos contextos |
| Integrations | adapters externos | IntegrationAccount | contextos por port |
| Audit | trilha de ações | AuditRecord | eventos de todos |

## 3. Invariantes
- Tenant, empresa e filial do agregado devem ser compatíveis.
- Quantidades e conversões usam decimal positivo e unidade explícita.
- Estoque muda somente por movimento.
- Venda concluída não é editada.
- Total pago não ultrapassa regra de troco/reembolso aplicável.
- Caixa fechado não aceita novo movimento.
- XML autorizado é imutável.
- Evento e comando crítico possuem ID idempotente.

## 4. Consistência
Invariantes dentro do agregado são transacionais. Efeitos entre contextos usam eventos e convergência observável. Estado pendente deve ser visível e reconciliável.

## 5. Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Contextos e invariantes iniciais. |

