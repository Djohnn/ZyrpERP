# PRD Operacional — Roadmap de Sprints do Zyrp

| Campo | Valor |
|---|---|
| Código | PRD-OPS-001 |
| Versão | 0.1.0 |
| Status | Review |
| Última atualização | 2026-07-14 |
| Produto | Zyrp |

## Finalidade

Este documento é o painel operacional de implementação do Zyrp. Ele permite acompanhar o andamento por sprint sem substituir as decisões normativas do PRD mestre, dos ADRs, da arquitetura, dos requisitos e da estratégia de segurança.

## Fontes obrigatórias

- [PRD mestre](01_Product/PRD-001_Master_v0.1.0.md)
- [Arquitetura de software](02_Architecture/SAD-001_Software_Architecture_v0.1.0.md)
- [Decisões arquiteturais](02_Architecture/ADR/)
- [Desenho de domínio](03_Domain/DDD-001_Domain_Design_v0.1.0.md)
- [Requisitos do sistema](04_Requirements/SRS-001_System_Requirements_v0.1.0.md)
- [Padrões de API](05_API/API-001_API_Standards_v0.1.0.md)
- [Estratégia de testes](07_Testing/TST-001_Test_Strategy_v0.1.0.md)
- [Segurança e multi-tenancy](08_Security/SEC-001_Security_Multitenancy_v0.1.0.md)
- [Operações e observabilidade](09_Operations/OPS-001_Operations_Observability_v0.1.0.md)

Em caso de conflito, o agente deve parar, informar a divergência e solicitar uma decisão. Mudança arquitetural exige ADR novo ou atualização formal de ADR existente.

## Como acompanhar

- `- [ ]`: tarefa pendente ou ainda não validada.
- `- [x]`: tarefa implementada e comprovada pela validação indicada.
- `BLOQUEADO:`: impedimento registrado abaixo da tarefa; a caixa permanece aberta.
- Uma tarefa parcialmente concluída continua aberta.
- O agente atualiza a caixa somente depois de executar a validação correspondente.
- Evidências devem ser registradas no relatório final da sprint e no histórico Git.

## Estado atual

| Sprint | Estado | Objetivo resumido |
|---:|---|---|
| 0 | Pronta para execução | Fundação técnica e isolamento multi-tenant |
| 1 | A detalhar | Autenticação, onboarding e autorização |
| 2 | A detalhar | Catálogo e cadastros-base |
| 3 | A detalhar | Estoque e movimentações |
| 4 | A detalhar | Vendas, pedidos e caixa web |
| 5 | A detalhar | PDV Electron online |
| 6 | A detalhar | Contingência offline e sincronização |
| 7 | A detalhar | Integração fiscal por provider |
| 8 | A detalhar | Piloto, observabilidade e hardening |

---

### Sprint 0 — Fundação Técnica do Zyrp

**Duração de referência:** 1 a 2 semanas  
**Estado:** Pronta para execução

**Objetivo:** disponibilizar uma base Django reproduzível, observável e testada, com autenticação preparada, hierarquia organizacional e isolamento multi-tenant comprovado antes da implementação dos módulos comerciais.

**Entregável:** o ambiente local inicia PostgreSQL, Redis e Django; `/health/` responde com sucesso; migrations executam do zero; e testes automatizados demonstram que um tenant não lê nem altera dados de outro.

**Decisões aplicáveis:** ADR-001, ADR-002, ADR-005 e ADR-006.

#### 0.1 Repositório e ambiente

- [ ] Criar os diretórios raiz `backend/`, `frontend/`, `pdv/` e `infra/`, cada um com README de responsabilidade.
- [ ] Definir Python 3.12 ou superior para o backend e registrar a versão suportada.
- [ ] Criar ambiente virtual local em `.venv/` sem versioná-lo.
- [ ] Criar `backend/pyproject.toml` ou arquivos equivalentes com Django, DRF, PostgreSQL, Redis, Celery, configuração e testes.
- [ ] Separar dependências de produção e desenvolvimento de forma reproduzível.
- [ ] Criar `.env.example` sem segredos, documentando todas as variáveis obrigatórias.
- [ ] Confirmar que `.env`, certificados, bancos SQLite, logs, volumes e builds são ignorados pelo Git.
- [ ] Documentar em `README.md` os comandos para preparar, iniciar, testar e parar o ambiente local.
- [ ] Validar instalação limpa das dependências em ambiente virtual novo.

**Validação 0.1:** executar a instalação documentada e confirmar `python --version`, importação do Django e `git status --short` sem artefatos locais.

#### 0.2 Infraestrutura local

- [ ] Criar `compose.yaml` para PostgreSQL e Redis usando versões fixadas.
- [ ] Configurar usuário, senha, database e portas somente por variáveis de ambiente.
- [ ] Adicionar health check real para PostgreSQL.
- [ ] Adicionar health check real para Redis.
- [ ] Definir volumes locais persistentes abrangidos pelo `.gitignore`.
- [ ] Configurar rede local sem expor serviços desnecessários.
- [ ] Criar comandos documentados para subir, inspecionar e parar a infraestrutura.
- [ ] Confirmar conexão do host com PostgreSQL e Redis.

**Validação 0.2:** `docker compose config` deve ser válido e `docker compose up -d` deve deixar PostgreSQL e Redis saudáveis.

#### 0.3 Backend Django e DRF

- [ ] Criar o projeto Django em `backend/` com pacote principal `config`.
- [ ] Separar settings em `base`, `local`, `test` e `production`.
- [ ] Ler configurações exclusivamente de variáveis de ambiente, com defaults apenas quando seguros localmente.
- [ ] Configurar PostgreSQL como banco principal; não usar SQLite como banco padrão do backend.
- [ ] Configurar Redis para cache e broker do Celery.
- [ ] Registrar Django REST Framework.
- [ ] Criar apps `core`, `accounts`, `tenancy`, `audit` e `outbox`.
- [ ] Configurar `LANGUAGE_CODE = "pt-br"` e `TIME_ZONE = "America/Sao_Paulo"`.
- [ ] Criar endpoint público `/health/` com status da aplicação e checagens sanitizadas de dependências.
- [ ] Criar middleware para `X-Correlation-ID`, reutilizando valor válido recebido ou gerando UUID.
- [ ] Retornar `X-Correlation-ID` em todas as respostas HTTP.
- [ ] Executar `python manage.py check` sem erros.

**Validação 0.3:** iniciar o servidor, consultar `/health/`, conferir HTTP 200 e o cabeçalho `X-Correlation-ID`.

#### 0.4 Identidade e estrutura multi-tenant

- [ ] Criar usuário customizado antes da primeira migration funcional.
- [ ] Usar e-mail normalizado como identificador de autenticação ou documentar formalmente alternativa aprovada.
- [ ] Criar modelos `Tenant`, `Company` e `Branch` conforme a hierarquia `Tenant → Empresa → Filial`.
- [ ] Criar modelo de membership entre usuário e tenant com papel e estado.
- [ ] Criar vínculo explícito do usuário com empresas e filiais autorizadas quando aplicável.
- [ ] Implementar modelo abstrato com UUID, `tenant_id`, `created_at` e `updated_at` para entidades tenant-scoped.
- [ ] Impedir `tenant_id` nulo em entidades pertencentes a tenant.
- [ ] Implementar resolução explícita do tenant ativo por requisição autenticada.
- [ ] Rejeitar requisição tenant-scoped sem contexto válido.
- [ ] Registrar migrations iniciais sem depender de dados manuais.
- [ ] Criar comando ou fixture segura para dados locais de demonstração com dois tenants.

**Validação 0.4:** recriar o banco vazio, executar migrations e criar dois tenants com empresas, filiais e usuários distintos.

#### 0.5 Isolamento, autorização e PostgreSQL RLS

- [ ] Definir política que filtre todas as entidades tenant-scoped pelo tenant ativo.
- [ ] Aplicar contexto do tenant na conexão PostgreSQL dentro de transação controlada.
- [ ] Criar policies RLS para pelo menos uma entidade tenant-scoped representativa.
- [ ] Habilitar e forçar RLS nas tabelas protegidas previstas no Sprint 0.
- [ ] Garantir negação segura quando a variável de contexto do tenant estiver ausente.
- [ ] Evitar queries globais em managers e serviços expostos a requisições.
- [ ] Implementar autorização de empresa e filial além do filtro de tenant.
- [ ] Padronizar resposta que não revele a existência de recurso pertencente a outro tenant.
- [ ] Criar teste de leitura cross-tenant bloqueada pela aplicação.
- [ ] Criar teste de leitura cross-tenant bloqueada pelo RLS.
- [ ] Criar teste de escrita cross-tenant bloqueada.
- [ ] Criar teste de IDOR para recurso de outro tenant.
- [ ] Criar teste que falha de forma segura sem contexto de tenant.

**Validação 0.5:** executar a suíte multi-tenant com PostgreSQL real e obter zero acessos indevidos entre os dois tenants de teste.

#### 0.6 Auditoria, Outbox e observabilidade mínima

- [ ] Configurar logs JSON estruturados sem segredos ou dados fiscais sensíveis.
- [ ] Incluir correlation ID, tenant ID, usuário e operação quando disponíveis.
- [ ] Criar modelo append-only de auditoria com ator, ação, recurso, instante e contexto.
- [ ] Registrar alterações administrativas relevantes sem armazenar senhas, tokens ou certificados.
- [ ] Criar modelo de Transactional Outbox com UUID, tipo, versão, aggregate, payload, instante e estado.
- [ ] Persistir evento de teste na Outbox na mesma transação da alteração de domínio.
- [ ] Criar processamento idempotente inicial para eventos da Outbox.
- [ ] Criar métrica ou log detectável para Outbox atrasada ou com falha.
- [ ] Testar rollback conjunto entre alteração de domínio e evento da Outbox.
- [ ] Testar que reprocessamento não duplica o efeito do evento.

**Validação 0.6:** testes provam atomicidade da Outbox, idempotência e presença do correlation ID nos logs e respostas.

#### 0.7 Qualidade, segurança e integração contínua

- [ ] Configurar formatter e linter Python com regras versionadas.
- [ ] Configurar verificação de tipos para o escopo adotado no Sprint 0.
- [ ] Configurar runner de testes com settings próprios e PostgreSQL.
- [ ] Configurar cobertura, sem usar porcentagem isolada como critério de qualidade.
- [ ] Criar testes unitários para regras puras de tenancy.
- [ ] Criar testes de integração para ORM, transações e RLS.
- [ ] Criar testes de API para autenticação, contexto, IDOR e correlation ID.
- [ ] Adicionar análise de dependências vulneráveis e segredos no pipeline.
- [ ] Criar pipeline de CI para instalar dependências, validar migrations, lintar e testar.
- [ ] Fazer o pipeline falhar quando migrations de models estiverem ausentes.
- [ ] Executar `python manage.py check --deploy` com settings de produção simulados.
- [ ] Documentar limitações conhecidas e riscos aceitos do Sprint 0.

**Validação 0.7:** pipeline completo passa em checkout limpo e nenhuma credencial aparece no repositório.

#### 0.8 Aceite e encerramento

- [ ] Executar `python manage.py check` e registrar saída sem erros.
- [ ] Executar verificação de migrations pendentes e obter resultado limpo.
- [ ] Executar toda a suíte de testes e obter zero falhas.
- [ ] Recriar o ambiente local seguindo somente o README.
- [ ] Validar `/health/` com PostgreSQL e Redis disponíveis.
- [ ] Validar isolamento entre dois tenants por aplicação e RLS.
- [ ] Revisar `git diff` para impedir segredos, certificados, dumps ou artefatos locais.
- [ ] Atualizar este checklist somente com tarefas efetivamente comprovadas.
- [ ] Registrar evidências, pendências e riscos no relatório final da sprint.
- [ ] Criar commit final `feat: sprint 0 - fundação técnica`.
- [ ] Parar e solicitar aprovação antes de detalhar ou iniciar o Sprint 1.

**Critérios de aceite da Sprint 0:**

- ambiente reproduzível a partir de checkout limpo;
- Django, PostgreSQL e Redis operacionais;
- usuário customizado e hierarquia organizacional migrados;
- contexto tenant obrigatório e RLS ativo nas tabelas protegidas;
- testes de isolamento, IDOR, Outbox e health check passando;
- CI executando as verificações obrigatórias;
- documentação local suficiente para outro desenvolvedor iniciar o projeto.

---

### Sprint 1 — Autenticação, Onboarding e Autorização

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** permitir criação controlada do tenant, entrada de usuários, recuperação de acesso, memberships e permissões por capability.  
**Entregável:** primeiro administrador cria sua organização e convida operadores com escopos de empresa e filial.

### Sprint 2 — Catálogo e Cadastros-base

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** implementar produtos, categorias, unidades, códigos, preços e cadastros comerciais essenciais.  
**Entregável:** catálogo isolado por tenant, preparado para casas de rações e expansão futura.

### Sprint 3 — Estoque e Movimentações

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** controlar saldo por filial por meio de movimentos imutáveis e operações idempotentes.  
**Entregável:** entradas, saídas, ajustes, transferências e rastreabilidade de estoque.

### Sprint 4 — Vendas, Pedidos e Caixa Web

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** realizar o ciclo comercial online com pedido, venda, pagamentos registrados e movimentação de caixa.  
**Entregável:** venda web consistente com estoque, financeiro, auditoria e Outbox.

### Sprint 5 — PDV Electron Online

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** disponibilizar caixa desktop online integrado às APIs do Zyrp.  
**Entregável:** operador abre caixa, vende, recebe e encerra turno no aplicativo Electron.

### Sprint 6 — Contingência Offline e Sincronização

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** manter vendas essenciais durante indisponibilidade breve e reconciliar com segurança.  
**Entregável:** journal SQLite restrito, sincronização idempotente e tratamento auditado de conflitos.

### Sprint 7 — Integração Fiscal

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** emitir NF-e/NFC-e por provedor externo atrás do contrato `FiscalProvider`.  
**Entregável:** configuração por cliente, emissão assíncrona, estados fiscais, retries e webhooks idempotentes.

### Sprint 8 — Piloto, Observabilidade e Hardening

**Estado:** A detalhar e aprovar antes de executar.  
**Objetivo:** preparar um piloto controlado com segurança, operação, suporte e recuperação verificáveis.  
**Entregável:** release candidata com SLOs iniciais, alertas, backup restaurado, runbooks e critérios de rollback.

---

## Registro de execução

Adicionar uma entrada somente ao encerrar cada sprint:

| Sprint | Data | Commit | Testes | Pendências ou riscos | Aprovação |
|---:|---|---|---|---|---|

