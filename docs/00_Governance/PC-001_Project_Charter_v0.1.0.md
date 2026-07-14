# PC-001 — Project Charter

| Campo | Valor |
|---|---|
| Código | PC-001 |
| Título | Project Charter |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Arquitetura de Software |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | DESIGN-FOUNDATION-001, PG-001 |
| Documentos relacionados | PV-001, PS-001, PRD-001, SAD-001 |

## 1. Mandato

Construir uma plataforma SaaS brasileira de gestão comercial, segura e extensível, começando por casas de rações e evoluindo por meio de um Core ERP reutilizável e módulos de segmento.

## 2. Problema

Pequenas e médias empresas operam vendas, estoque, compras, caixa, financeiro e fiscal em ferramentas fragmentadas. Isso provoca divergências, baixa rastreabilidade, retrabalho e dependência de processos manuais, especialmente quando há múltiplas filiais ou indisponibilidade de internet no caixa.

## 3. Objetivos

- Unificar o ciclo comercial e fiscal.
- Preservar rastreabilidade de estoque, dinheiro e documentos fiscais.
- Operar como SaaS multiempresa e multifilial.
- Manter vendas durante falhas de conexão por contingência restrita.
- Permitir expansão por segmento sem duplicar o Core.
- Preparar APIs e eventos para integrações e IA futura.

## 4. Não objetivos do MVP

- Microsserviços.
- Integração fiscal direta com todas as SEFAZ.
- IA, agentes ou RAG em produção.
- Marketplace, CRM avançado ou aplicativo móvel completo.
- BI preditivo e automação autônoma de decisões críticas.
- Operação administrativa integralmente offline.

## 5. Escopo do MVP

Identity, Organizations, Catalog, Inventory, Purchasing, Sales, PDV, Cash Management, Financial, Fiscal, Analytics operacional, Integrations e Audit. O MVP deve suportar NF-e/NFC-e, PDV Electron e hierarquia `Tenant → Empresa → Filial`.

## 6. Modelo fiscal

Cada empresa cliente contratará e pagará o próprio provedor fiscal, certificado e credenciais. O ERP fornecerá uma integração desacoplada, emissão, acompanhamento, armazenamento e impressão. A centralização desse custo poderá ser reavaliada após validação comercial e escala.

## 7. Stakeholders

- Proprietário e gestor do estabelecimento.
- Operador de caixa e estoquista.
- Comprador e financeiro.
- Contador e responsável fiscal.
- Administrador do tenant.
- Operação e suporte da plataforma.
- Provedores fiscais, pagamentos e infraestrutura.

## 8. Premissas

- Lançamento inicial no Brasil.
- PostgreSQL compartilhado com RLS.
- Monólito modular Django.
- PDV online por padrão, com contingência restrita.
- Cliente possui orientação contábil para parametrização tributária.
- Infraestrutura externa possui ambientes de homologação.

## 9. Restrições

- LGPD e retenção legal de documentos fiscais.
- Regras fiscais variam por UF e documento.
- Operações offline não conhecem o estoque global em tempo real.
- O MVP deve controlar custos operacionais por tenant.
- Dados e credenciais de um tenant jamais podem atravessar fronteiras.

## 10. Riscos principais

| Risco | Mitigação inicial |
|---|---|
| Vazamento entre tenants | Escopo de aplicação, RLS e testes negativos |
| Duplicidade de venda/nota | UUID, idempotência e Outbox |
| Perda de venda offline | SQLite WAL, fila persistente e reconciliação |
| Rejeição fiscal | Máquina de estados, painel e correção assistida |
| Escopo excessivo | Milestones, capabilities e gates de aceite |
| Dependência de fornecedor | Ports/adapters e ADR de seleção |

## 11. Métricas de sucesso do piloto

- Zero incidentes de isolamento entre tenants.
- Zero perda confirmada de venda após falha controlada.
- Nenhuma duplicidade fiscal causada por reenvio.
- Fechamentos de caixa rastreáveis por forma de pagamento.
- Inventário e vendas conciliáveis por filial.
- Tempo e disponibilidade medidos por SLOs antes do lançamento.

## 12. Critério para iniciar código

Foundation Design, governança, PRD Master, SAD, DDD, SRS, segurança e estratégia de testes devem estar completos em Draft, consistentes e revisados. ADRs fundamentais devem estar aprovados.

## 13. Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Primeiro charter controlado. |
