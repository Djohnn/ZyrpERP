# PS-001 — Product Strategy

| Campo | Valor |
|---|---|
| Código | PS-001 |
| Título | Product Strategy |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Produto e Arquitetura |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | PV-001, PC-001 |
| Documentos relacionados | PB-001, PRD-001, REL-001 |

## 1. Estratégia

Entrar por um segmento com dor operacional concreta — casas de rações — e validar um Core ERP reutilizável antes de expandir. A diferenciação virá da combinação entre especialização suficiente, segurança SaaS e operação de PDV resiliente.

## 2. Beachhead market

Estabelecimentos brasileiros que vendem produtos no balcão, controlam estoque, realizam compras recorrentes, trabalham com unidades fechadas ou fracionadas e emitem NF-e/NFC-e.

## 3. Fases

| Fase | Objetivo | Evidência de avanço |
|---|---|---|
| Foundation | Documentos e contratos coerentes | Revisão cruzada concluída |
| Technical MVP | Fluxos integrados em homologação | Gates técnicos atendidos |
| Pilot | Operação controlada em 1–2 lojas | Vendas, caixa e fiscal conciliados |
| Commercial MVP | Primeiros clientes pagantes | SLOs e suporte sustentáveis |
| Expansion | Novos segmentos e integrações | Core reutilizado sem forks |

## 4. Posicionamento

ERP comercial SaaS com profundidade operacional para o varejo especializado. Não competirá inicialmente por gratuidade total nem por cobrir todos os segmentos. O produto priorizará confiança, rastreabilidade e suporte ao fluxo real.

## 5. Modelo de valor

- Assinatura por tenant com limites transparentes.
- Capacidade multiempresa e multifilial conforme plano futuro.
- Provedor fiscal e certificado pagos pelo cliente no MVP.
- Serviços de implantação e suporte avançado podem ser adicionais.
- Não subsidiar emissão fiscal antes de escala e validação econômica.

## 6. Diferenciais planejados

- Produto fracionado e conversão de unidades.
- PDV online com contingência offline segura.
- Estoque e caixa baseados em movimentos auditáveis.
- Fiscal por adapters substituíveis.
- Multi-tenancy com RLS e testes de isolamento.
- Futuro copiloto de IA sem dependência no MVP.

## 7. Expansão

Após casas de rações: agropecuárias, pet shops, embalagens e ferragens. Cada expansão exige discovery próprio, ADR quando afetar o Core e módulo de segmento quando a regra não for universal.

## 8. Métricas

- Tempo de implantação.
- Taxa de venda concluída sem intervenção.
- Divergência de caixa e estoque.
- Rejeição fiscal por causa controlável.
- Operações offline conciliadas.
- Disponibilidade e latência percebida.
- Retenção e adoção por capability.

## 9. Riscos estratégicos

- MVP amplo demais: dividir por milestones verticais.
- Complexidade fiscal: provedor externo e rollout por UF.
- Comparação com ERP gratuito: competir por confiabilidade e serviço.
- Customizações por cliente: parametrizar sem criar forks.

## 10. Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Primeira estratégia controlada. |

