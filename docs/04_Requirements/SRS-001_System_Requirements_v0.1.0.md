# SRS-001 — System Requirements Specification

| Campo | Valor |
|---|---|
| Código | SRS-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | PRD-001, SAD-001, DDD-001 |
| Última atualização | 2026-07-14 |

## Requisitos funcionais
| ID | Requisito | Prioridade | Aceite resumido |
|---|---|---|---|
| FR-PLATFORM-001 | Manter tenant e estado da assinatura | Must | Tenant suspenso não opera |
| FR-IDENTITY-001 | Autenticar usuário e aplicar associação contextual | Must | Acesso fora da associação é negado |
| FR-ORG-001 | Manter empresas e filiais do tenant | Must | Relações cross-tenant são rejeitadas |
| FR-CATALOG-001 | Manter produto, unidade e conversão | Must | Conversão positiva e versionada |
| FR-INVENTORY-001 | Registrar todo ajuste como movimento | Must | Saldo deriva dos movimentos |
| FR-PURCHASING-001 | Registrar pedido e recebimento parcial/total | Must | Recebimento gera estoque e obrigação |
| FR-SALES-001 | Concluir venda com itens, descontos e pagamentos | Must | Totais e estado ficam imutáveis |
| FR-PDV-001 | Registrar dispositivo e sincronizar lote idempotente | Must | Reenvio não duplica operação |
| FR-CASH-001 | Abrir, movimentar e fechar sessão | Must | Diferença é registrada e auditada |
| FR-FINANCIAL-001 | Controlar contas e liquidações | Must | Saldo reflete lançamentos imutáveis |
| FR-FISCAL-001 | Emitir NF-e/NFC-e por FiscalProvider | Must | Estado e artefatos ficam auditados |
| FR-FISCAL-002 | Processar cancelamento e rejeição separadamente | Must | Rejeição não recebe retry cego |
| FR-AUDIT-001 | Registrar ação sensível com ator e contexto | Must | Registro não pode ser alterado |
| FR-ANALYTICS-001 | Exibir indicadores operacionais por escopo | Should | Filtros respeitam tenant/filial |

## Requisitos não funcionais
| ID | Requisito | Prioridade | Aceite resumido |
|---|---|---|---|
| NFR-SECURITY-001 | Isolar tenants em aplicação e RLS | Must | Testes negativos com dois tenants passam |
| NFR-SECURITY-002 | Criptografar segredos e proibir logs sensíveis | Must | Scanner não encontra credenciais |
| NFR-RELIABILITY-001 | Operações críticas são idempotentes | Must | Retry repetido produz um resultado |
| NFR-RELIABILITY-002 | Backup possui restauração testada | Must | Restore periódico é evidenciado |
| NFR-OFFLINE-001 | Venda local sobrevive a reinício abrupto | Must | Journal recupera operação pendente |
| NFR-PERFORMANCE-001 | Definir e medir SLOs antes do piloto | Must | Dashboard contém latência/erro/saturação |
| NFR-OBSERVABILITY-001 | Correlation ID atravessa HTTP, job e evento | Must | Trilha ponta a ponta é consultável |
| NFR-MAINTAINABILITY-001 | Módulos respeitam dependências documentadas | Must | Teste arquitetural bloqueia violação |
| NFR-PRIVACY-001 | Aplicar classificação, retenção e direitos LGPD | Must | Fluxos documentados e auditáveis |

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Requisitos mestres iniciais. |

