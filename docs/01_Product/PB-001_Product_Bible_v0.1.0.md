# PB-001 — Product Bible

| Campo | Valor |
|---|---|
| Código | PB-001 |
| Título | Product Bible |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Produto e Arquitetura |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | PV-001, PS-001 |
| Documentos relacionados | PRD-001, DDD-001, SRS-001 |

## 1. Finalidade

Ser a referência canônica de linguagem, princípios e regras transversais do produto. Documentos de capability podem detalhar, mas não contradizer este vocabulário sem ADR e revisão do Product Bible.

## 2. Tenant

Conta SaaS que delimita propriedade, faturamento, usuários, configuração e isolamento de dados. Um tenant possui uma ou mais empresas. `tenant_id` acompanha toda entidade de negócio, tarefa, evento, cache e arquivo.

## 3. Empresa

Entidade legal ou operacional pertencente a um tenant. Possui dados cadastrais, CNPJ, regime tributário, certificado e configuração fiscal próprios. Uma empresa possui uma ou mais filiais.

## 4. Filial

Unidade operacional vinculada a uma empresa. Define contexto de estoque, caixa, PDV, série fiscal quando aplicável e relatórios locais.

## 5. Usuário

Identidade humana global autenticável. Acesso nasce de associação ao tenant e de papéis concedidos por empresa, filial e função. Usuário não recebe acesso por conhecer IDs de recursos.

## 6. Produto

Item comercializável com identidade, descrição, categoria, unidade base, códigos, preço e dados fiscais. Variações são identidades comercializáveis relacionadas, não texto livre.

## 7. Unidade e fracionamento

A unidade base controla estoque. Unidades comerciais convertem para a base por fator explícito e versionado. Uma venda preserva unidade, fator e quantidade usados naquele momento.

## 8. Estoque

Resultado de movimentos imutáveis por tenant, filial, produto e localização. O saldo é projeção; ajustes geram movimentos e nunca sobrescrevem histórico.

## 9. Compra

Compromisso de aquisição junto a fornecedor. Pedido, recebimento, entrada de estoque, obrigação financeira e documento fiscal são estados relacionados, porém distintos.

## 10. Venda

Transação comercial composta por itens, descontos, pagamentos e contexto operacional. Uma venda concluída é fato imutável; correções ocorrem por cancelamento, devolução, estorno ou documento compensatório.

## 11. Caixa

Sessão operacional vinculada a filial, dispositivo e operador responsável. Abertura, reforço, sangria, recebimento e fechamento são movimentos auditáveis. Caixa físico não se confunde com conta financeira.

## 12. Documento Fiscal

Representação fiscal associada a uma operação, com ciclo próprio. XML autorizado é o documento eletrônico normativo e não pode ser alterado. DANFE/DANFC-e é representação auxiliar para consulta e impressão.

## 13. Dispositivo PDV

Instalação registrada do Electron vinculada a tenant, empresa, filial e caixa. Possui credencial revogável própria e armazena apenas dados mínimos. O PDV opera online por padrão.

## 14. Contingência offline

Modo temporário e restrito para continuidade de venda. Não autoriza administração offline nem resolve magicamente o estoque global. Toda operação local entra em journal persistente e exige conciliação.

## 15. Core ERP e módulo de segmento

O Core contém regras universais de identidade, organização, catálogo, estoque, compras, vendas, caixa, financeiro, fiscal e auditoria. Regra específica de casas de rações entra em módulo de segmento quando não for universal.

## 16. Provedor fiscal

Serviço externo acessado por um port. No MVP, o cliente contrata e paga o provedor e o certificado. O Core Fiscal não depende de marca específica.

## 17. Inteligência artificial

Capacidade futura. O MVP não depende de IA. Evolução prevista: RAG documental, copiloto somente leitura, recomendações, ações com aprovação e agentes especializados. IA nunca recebe acesso irrestrito ao banco.

## 18. Regras canônicas

1. Dinheiro usa decimal e moeda explícita.
2. Datas persistem em UTC; calendário de negócio respeita fuso da empresa.
3. Operação crítica é idempotente e auditável.
4. Contexto de tenant é explícito e validado em profundidade.
5. Estados pendentes, rejeitados ou não sincronizados são visíveis.
6. Exclusão não apaga fatos contábeis, financeiros, fiscais ou de estoque.
7. Fornecedor externo é isolado por adapter.

## 19. Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Vocabulário e princípios canônicos iniciais. |
