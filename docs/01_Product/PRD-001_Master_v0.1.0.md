# PRD-001 — Master Product Requirements

| Campo | Valor |
|---|---|
| Código | PRD-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Produto e Arquitetura |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | PV-001, PS-001, PB-001, PC-001 |
| Documentos relacionados | SRS-001, SAD-001, DDD-001 |

## 1. Produto
SaaS brasileiro de gestão comercial para casas de rações, estruturado como Core ERP e módulos de segmento.

## 2. Problemas
Dados fragmentados, estoque impreciso, caixa não conciliado, baixa rastreabilidade fiscal, operação vulnerável à internet e dificuldade multiempresa.

## 3. Personas e jornadas
- Proprietário: acompanhar resultado, risco e operação por filial.
- Gerente: configurar equipe, preços e processos.
- Caixa: abrir sessão, vender, receber, emitir e fechar.
- Estoquista/comprador: repor, receber, contar e transferir.
- Financeiro: controlar obrigações, liquidações e fluxo.
- Contador: acessar documentos e informações fiscais.

## 4. Capabilities do MVP
Platform, Identity, Organizations, Catalog, Inventory, Purchasing, Sales, PDV, Cash Management, Financial, Fiscal, Analytics operacional, Integrations e Audit.

## 5. Jornadas críticas
1. Onboarding de tenant, empresa, filial, usuários e configuração fiscal.
2. Cadastro de produto com unidade base, conversão, preço e tributação.
3. Compra → recebimento → estoque → obrigação financeira.
4. Abertura de caixa → venda → pagamento → fiscal → fechamento.
5. Devolução/estorno com reflexos rastreáveis.
6. Venda em contingência → sincronização → conciliação.

## 6. Regras de produto
- Hierarquia `Tenant → Empresa → Filial`.
- Estoque muda por movimento; venda concluída não é editada.
- PDV é online por padrão; offline limita-se ao fluxo essencial.
- Cliente paga provedor fiscal e certificado no MVP.
- XML autorizado é imutável.
- IA permanece fora do MVP.

## 7. Fora do escopo
Microsserviços, integração fiscal direta nacional, IA/RAG, CRM avançado, marketplace, aplicativo móvel completo, BI preditivo e administração integralmente offline.

## 8. Critérios de sucesso
Zero vazamento cross-tenant, nenhuma duplicidade por retry, venda offline recuperável, caixa conciliável, estoque rastreável, emissão fiscal auditável e SLOs medidos antes da produção.

## 9. Riscos
Escopo amplo, fiscal por UF, conflito offline, configuração tributária incorreta e lock-in externo. Mitigações estão nos ADRs, SEC-001 e TST-001.

## 10. Roadmap
Foundation → Technical MVP → Pilot em 1–2 lojas → Commercial MVP → Expansion. PRDs por capability detalharão cada vertical antes do código correspondente.

## 11. Aceite do MVP
Todas as jornadas críticas executam em staging; requisitos Must passam; isolamento, backup, fiscal, sincronização e rollback são demonstrados; documentação e runbooks estão atualizados.

## 12. Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | PRD Master inicial. |

