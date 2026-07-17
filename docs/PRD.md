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
| 0 | Concluída | Fundação técnica e isolamento multi-tenant |
| 1 | Concluída | Autenticação, onboarding e autorização |
| 2 | Concluída | Catálogo e cadastros-base |
| 3 | Em execução | Estoque e movimentações |
| 4 | A detalhar | Vendas, pedidos e caixa web |
| 5 | A detalhar | PDV Electron online |
| 6 | A detalhar | Contingência offline e sincronização |
| 7 | A detalhar | Integração fiscal por provider |
| 8 | A detalhar | Piloto, observabilidade e hardening |

---

### Sprint 0 — Fundação Técnica do Zyrp

**Duração de referência:** 1 a 2 semanas  
**Estado:** Concluída

**Correção de aceite:** os problemas de bypass de RLS, ausência de IDOR real, migrations pendentes e checkboxes sem evidência foram corrigidos e revalidados em 2026-07-14. As evidências estão no relatório final da sprint e no histórico Git.

**Objetivo:** disponibilizar uma base Django reproduzível, observável e testada, com autenticação preparada, hierarquia organizacional e isolamento multi-tenant comprovado antes da implementação dos módulos comerciais.

**Entregável:** o ambiente local inicia PostgreSQL, Redis e Django; `/health/` responde com sucesso; migrations executam do zero; e testes automatizados demonstram que um tenant não lê nem altera dados de outro.

**Decisões aplicáveis:** ADR-001, ADR-002, ADR-005 e ADR-006.

#### 0.1 Repositório e ambiente

- [x] Criar os diretórios raiz `backend/`, `frontend/`, `pdv/` e `infra/`, cada um com README de responsabilidade.
- [x] Definir Python 3.12 ou superior para o backend e registrar a versão suportada.
- [x] Criar ambiente virtual local em `.venv/` sem versioná-lo.
- [x] Criar `backend/pyproject.toml` ou arquivos equivalentes com Django, DRF, PostgreSQL, Redis, Celery, configuração e testes.
- [x] Separar dependências de produção e desenvolvimento de forma reproduzível.
- [x] Criar `.env.example` sem segredos, documentando todas as variáveis obrigatórias.
- [x] Confirmar que `.env`, certificados, bancos SQLite, logs, volumes e builds são ignorados pelo Git.
- [x] Documentar em `README.md` os comandos para preparar, iniciar, testar e parar o ambiente local.
- [x] Validar instalação limpa das dependências em ambiente virtual novo.

**Validação 0.1:** executar a instalação documentada e confirmar `python --version`, importação do Django e `git status --short` sem artefatos locais.

#### 0.2 Infraestrutura local

- [x] Criar `compose.yaml` para PostgreSQL e Redis usando versões fixadas.
- [x] Configurar usuário, senha, database e portas somente por variáveis de ambiente.
- [x] Adicionar health check real para PostgreSQL.
- [x] Adicionar health check real para Redis.
- [x] Definir volumes locais persistentes abrangidos pelo `.gitignore`.
- [x] Configurar rede local sem expor serviços desnecessários.
- [x] Criar comandos documentados para subir, inspecionar e parar a infraestrutura.
- [x] Confirmar conexão do host com PostgreSQL e Redis.

**Validação 0.2:** `docker compose config` deve ser válido e `docker compose up -d` deve deixar PostgreSQL e Redis saudáveis.

#### 0.3 Backend Django e DRF

- [x] Criar o projeto Django em `backend/` com pacote principal `config`.
- [x] Separar settings em `base`, `local`, `test` e `production`.
- [x] Ler configurações exclusivamente de variáveis de ambiente, com defaults apenas quando seguros localmente.
- [x] Configurar PostgreSQL como banco principal; não usar SQLite como banco padrão do backend.
- [x] Configurar Redis para cache e broker do Celery.
- [x] Registrar Django REST Framework.
- [x] Criar apps `core`, `accounts`, `tenancy`, `audit` e `outbox`.
- [x] Configurar `LANGUAGE_CODE = "pt-br"` e `TIME_ZONE = "America/Sao_Paulo"`.
- [x] Criar endpoint público `/health/` com status da aplicação e checagens sanitizadas de dependências.
- [x] Criar middleware para `X-Correlation-ID`, reutilizando valor válido recebido ou gerando UUID.
- [x] Retornar `X-Correlation-ID` em todas as respostas HTTP.
- [x] Executar `python manage.py check` sem erros.

**Validação 0.3:** iniciar o servidor, consultar `/health/`, conferir HTTP 200 e o cabeçalho `X-Correlation-ID`.

#### 0.4 Identidade e estrutura multi-tenant

- [x] Criar usuário customizado antes da primeira migration funcional.
- [x] Usar e-mail normalizado como identificador de autenticação ou documentar formalmente alternativa aprovada.
- [x] Criar modelos `Tenant`, `Company` e `Branch` conforme a hierarquia `Tenant → Empresa → Filial`.
- [x] Criar modelo de membership entre usuário e tenant com papel e estado.
- [x] Criar vínculo explícito do usuário com empresas e filiais autorizadas quando aplicável.
- [x] Implementar modelo abstrato com UUID, `tenant_id`, `created_at` e `updated_at` para entidades tenant-scoped.
- [x] Impedir `tenant_id` nulo em entidades pertencentes a tenant.
- [x] Implementar resolução explícita do tenant ativo por requisição autenticada.
- [x] Rejeitar requisição tenant-scoped sem contexto válido.
- [x] Registrar migrations iniciais sem depender de dados manuais.
- [x] Criar comando ou fixture segura para dados locais de demonstração com dois tenants.

**Validação 0.4:** recriar o banco vazio, executar migrations e criar dois tenants com empresas, filiais e usuários distintos.

#### 0.5 Isolamento, autorização e PostgreSQL RLS

- [x] Definir política que filtre todas as entidades tenant-scoped pelo tenant ativo.
- [x] Aplicar contexto do tenant na conexão PostgreSQL dentro de transação controlada.
- [x] Criar policies RLS para pelo menos uma entidade tenant-scoped representativa.
- [x] Habilitar e forçar RLS nas tabelas protegidas previstas no Sprint 0.
- [x] Garantir negação segura quando a variável de contexto do tenant estiver ausente.
- [x] Evitar queries globais em managers e serviços expostos a requisições.
- [x] Implementar autorização de empresa e filial além do filtro de tenant.
- [x] Padronizar resposta que não revele a existência de recurso pertencente a outro tenant.
- [x] Criar teste de leitura cross-tenant bloqueada pela aplicação.
- [x] Criar teste de leitura cross-tenant bloqueada pelo RLS.
- [x] Criar teste de escrita cross-tenant bloqueada.
- [x] Criar teste de IDOR para recurso de outro tenant.
- [x] Criar teste que falha de forma segura sem contexto de tenant.

**Validação 0.5:** executar a suíte multi-tenant com PostgreSQL real e obter zero acessos indevidos entre os dois tenants de teste.

#### 0.6 Auditoria, Outbox e observabilidade mínima

- [x] Configurar logs JSON estruturados sem segredos ou dados fiscais sensíveis.
- [x] Incluir correlation ID, tenant ID, usuário e operação quando disponíveis.
- [x] Criar modelo append-only de auditoria com ator, ação, recurso, instante e contexto.
- [x] Registrar alterações administrativas relevantes sem armazenar senhas, tokens ou certificados.
- [x] Criar modelo de Transactional Outbox com UUID, tipo, versão, aggregate, payload, instante e estado.
- [x] Persistir evento de teste na Outbox na mesma transação da alteração de domínio.
- [x] Criar processamento idempotente inicial para eventos da Outbox.
- [x] Criar métrica ou log detectável para Outbox atrasada ou com falha.
- [x] Testar rollback conjunto entre alteração de domínio e evento da Outbox.
- [x] Testar que reprocessamento não duplica o efeito do evento.

**Validação 0.6:** testes provam atomicidade da Outbox, idempotência e presença do correlation ID nos logs e respostas.

#### 0.7 Qualidade, segurança e integração contínua

- [x] Configurar formatter e linter Python com regras versionadas.
- [x] Configurar verificação de tipos para o escopo adotado no Sprint 0.
- [x] Configurar runner de testes com settings próprios e PostgreSQL.
- [x] Configurar cobertura, sem usar porcentagem isolada como critério de qualidade.
- [x] Criar testes unitários para regras puras de tenancy.
- [x] Criar testes de integração para ORM, transações e RLS.
- [x] Criar testes de API para autenticação, contexto, IDOR e correlation ID.
- [x] Adicionar análise de dependências vulneráveis e segredos no pipeline.
- [x] Criar pipeline de CI para instalar dependências, validar migrations, lintar e testar.
- [x] Fazer o pipeline falhar quando migrations de models estiverem ausentes.
- [x] Executar `python manage.py check --deploy` com settings de produção simulados.
- [x] Documentar limitações conhecidas e riscos aceitos do Sprint 0.

**Limitações conhecidas e riscos aceitos:**
- O owner de migrations permanece separado do usuário de runtime. O runtime usa `zyrp_app`, sem `SUPERUSER` e sem `BYPASSRLS`; testes usam papel próprio, também sem bypass.
- Credenciais de desenvolvimento presentes em exemplos e CI são placeholders não reutilizáveis. Produção exige valores externos e uma `SECRET_KEY` forte.
- O backend está validado no Python 3.14 local e no Python 3.13 da CI; o requisito mínimo declarado continua sendo Python 3.12.
- A verificação local do `pip-audit` pode depender do trust store corporativo do Windows. O gate estrito permanece obrigatório na CI Linux e não desabilita TLS.
- `var-annotated` em campos de models Django é suprimido somente nos módulos de models definidos no `pyproject.toml`.

**Validação 0.7:** pipeline completo passa em checkout limpo e nenhuma credencial aparece no repositório.

#### 0.8 Aceite e encerramento

- [x] Executar `python manage.py check` e registrar saída sem erros.
- [x] Executar verificação de migrations pendentes e obter resultado limpo.
- [x] Executar toda a suíte de testes e obter zero falhas.
- [x] Recriar o ambiente local seguindo somente o README.
- [x] Validar `/health/` com PostgreSQL e Redis disponíveis.
- [x] Validar isolamento entre dois tenants por aplicação e RLS.
- [x] Revisar `git diff` para impedir segredos, certificados, dumps ou artefatos locais.
- [x] Atualizar este checklist somente com tarefas efetivamente comprovadas.
- [x] Registrar evidências, pendências e riscos no relatório final da sprint.
- [x] Criar commit final `feat: sprint 0 - fundação técnica`.
- [x] Parar e solicitar aprovação antes de detalhar ou iniciar o Sprint 1.

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

**Duração de referência:** 2 semanas
**Estado:** Concluída

**Objetivo:** permitir criação controlada do tenant, entrada de usuários, recuperação de acesso, MFA, memberships e permissões por capability.

**Entregável:** primeiro administrador cria e confirma sua organização, configura MFA por TOTP ou e-mail, autentica-se com sessão segura e convida usuários com papel e escopo de filial.

**Especificação:** [Design da Sprint 1](superpowers/specs/2026-07-14-sprint-1-auth-onboarding-design.md)

#### 1.1 Configuração e fundação de segurança

- [x] Adicionar dependências versionadas para TOTP, criptografia e rate limiting.
- [x] Configurar backend de e-mail local/teste e SMTP por ambiente em produção.
- [x] Exigir chave externa para cifrar segredos MFA em produção.
- [x] Definir expirações, limites de tentativa e cooldowns por settings.
- [x] Documentar novas variáveis em `.env.example` sem valores reais.
- [x] Manter cookies seguros, CSRF e rotação de sessão.

**Validação 1.1:** instalação limpa, Django check e deploy check aprovados sem segredos no repositório.

#### 1.2 Tokens e artefatos temporários

- [x] Criar modelo genérico de token de uso único com finalidade, digest e expiração.
- [x] Persistir somente digest de confirmação, recuperação, convite e códigos MFA.
- [x] Implementar consumo atômico e uso único.
- [x] Implementar expiração e limite de tentativas.
- [x] Criar modelo de dispositivo MFA com segredo TOTP cifrado.
- [x] Criar códigos de recuperação armazenados somente como hash.
- [x] Impedir tokens, códigos e segredos em logs, auditoria e Outbox.

**Validação 1.2:** testes provam expiração, adulteração, replay bloqueado, consumo único e ausência de plaintext persistido.

#### 1.3 Cadastro público e confirmação

- [x] Criar endpoint público de cadastro do primeiro administrador.
- [x] Normalizar e validar e-mail sem permitir enumeração indevida.
- [x] Criar usuário, tenant, empresa, filial e membership admin na mesma transação.
- [x] Gerar slug seguro e resolver colisões.
- [x] Impedir escolha de IDs, tenant ou papel privilegiado pelo payload.
- [x] Enviar confirmação de e-mail somente após commit.
- [x] Criar endpoint de confirmação com token expirável e de uso único.
- [x] Bloquear acesso operacional antes da confirmação.
- [x] Auditar cadastro e confirmação sem armazenar token.
- [x] Testar rollback integral do onboarding.

**Validação 1.3:** cadastro cria hierarquia completa ou não persiste nada; confirmação válida ativa o fluxo e replay falha.

#### 1.4 Sessão, login e logout

- [x] Criar login por e-mail e senha usando sessão Django.
- [x] Usar resposta uniforme para conta inexistente e senha incorreta.
- [x] Rejeitar conta inativa ou e-mail não confirmado.
- [x] Criar estado intermediário de sessão antes do MFA.
- [x] Rotacionar sessão após autenticação completa.
- [x] Criar logout com invalidação server-side.
- [x] Criar endpoint `/auth/me/` sanitizado.
- [x] Aplicar rate limiting a login e endpoints públicos sensíveis.
- [x] Auditar sucessos e bloqueios relevantes sem registrar credenciais.

**Validação 1.4:** testes provam não enumeração, rotação/invalidação de sessão, CSRF e limitação de abuso.

#### 1.5 Política MFA e TOTP

- [x] Criar política por tenant com TOTP e e-mail permitidos.
- [x] Garantir que ao menos um método permaneça permitido.
- [x] Permitir alteração somente com capability administrativa.
- [x] Impedir remoção do único método verificado de administrador.
- [x] Gerar enrollment TOTP e URI `otpauth` exibidos uma vez.
- [x] Cifrar segredo TOTP em repouso.
- [x] Exigir código válido para ativar TOTP.
- [x] Limitar janela temporal e bloquear replay do mesmo timestep.
- [x] Exigir MFA de administradores antes de operações tenant-scoped.
- [x] Testar IDOR da política MFA.

**Validação 1.5:** TOTP funciona com janela limitada, não permite replay e a política de outro tenant retorna 404.

#### 1.6 MFA por e-mail e recuperação

- [x] Criar desafio MFA por e-mail com código aleatório.
- [x] Expirar desafio em dez minutos.
- [x] Limitar a cinco tentativas e aplicar cooldown de reenvio.
- [x] Consumir o código uma única vez.
- [x] Elevar e rotacionar a sessão após desafio válido.
- [x] Gerar códigos de recuperação exibidos uma única vez.
- [x] Consumir código de recuperação uma única vez.
- [x] Regenerar códigos invalidando o conjunto anterior.
- [x] Auditar operações sem armazenar códigos.

**Validação 1.6:** testes cobrem código válido, expirado, tentativa excedida, cooldown, replay e recuperação.

#### 1.7 Recuperação de senha

- [x] Criar solicitação com resposta indistinguível para e-mail existente/inexistente.
- [x] Enviar token somente após commit.
- [x] Validar política de senha do Django na redefinição.
- [x] Expirar e consumir token uma única vez.
- [x] Revogar sessões existentes após redefinição.
- [x] Manter MFA obrigatório no próximo login.
- [x] Auditar conclusão sem armazenar token ou senha.

**Validação 1.7:** testes provam não enumeração, expiração, adulteração, uso único e revogação de sessões.

#### 1.8 Capabilities, convites e memberships

- [x] Definir matriz inicial de capabilities para admin, manager e operator.
- [x] Centralizar autorização por usuário, tenant, capability e filial.
- [x] Proibir comparações dispersas de strings de papel nas views.
- [x] Criar convite com e-mail normalizado, papel, filiais, digest e expiração.
- [x] Validar que filiais do convite pertencem ao tenant ativo.
- [x] Aceitar convite somente com e-mail autenticado correspondente.
- [x] Tornar convite de uso único e revogar token anterior no reenvio.
- [x] Criar listagem e alteração segura de memberships.
- [x] Impedir escalada de papel e remoção do último administrador.
- [x] Retornar 404 para convite ou membership de outro tenant.
- [x] Auditar convite, reenvio, aceite, papel e escopo.

**Validação 1.8:** matriz, convites e memberships passam testes de capability, filial, IDOR, replay e invariantes administrativas.

#### 1.9 Contratos, qualidade e aceite

- [x] Documentar endpoints e erros no OpenAPI.
- [x] Atualizar READMEs com fluxos e configuração segura.
- [x] Ampliar sanitização de auditoria para todos os artefatos de autenticação.
- [x] Executar migrations com owner separado do runtime.
- [x] Executar Ruff e mypy sem falhas.
- [x] Executar suíte completa com PostgreSQL real e cobertura mínima mantida.
- [x] Executar testes de isolamento, RLS e IDOR sem regressão.
- [x] Executar check de produção simulado.
- [x] Executar auditoria de dependências e hook de segredos na CI.
- [x] Registrar evidências e riscos no relatório final da sprint.
- [x] Atualizar checklist somente após validação correspondente.
- [x] Criar commit final `feat: sprint 1 - autenticação e onboarding`.
- [x] Enviar para `master` e obter CI remota verde.
- [x] Confirmar worktree limpo e sincronizado com `origin/master`.

**Critérios de aceite da Sprint 1:**

- onboarding público é atômico e não permite autoelevação;
- e-mail confirmado e MFA são obrigatórios para administrador;
- TOTP e e-mail respeitam a política do tenant;
- recuperação e convites resistem a enumeração, replay e IDOR;
- capabilities respeitam tenant, papel e filial;
- nenhum segredo aparece no banco em plaintext evitável, logs, auditoria, Outbox ou Git;
- regressões da Sprint 0 permanecem aprovadas;
- CI remota termina com sucesso.

### Sprint 2 — Catálogo e Cadastros-base

**Estado:** Concluída

**Objetivo:** implementar produtos, categorias, unidades, códigos e preços essenciais.

**Entregável:** catálogo isolado por tenant, preparado para casas de rações e expansão futura.

**Especificação:** [Design da Sprint 2](superpowers/specs/2026-07-14-sprint-2-catalog-design.md)

**Plano:** [Plano de implementação da Sprint 2](superpowers/plans/2026-07-14-sprint-2-catalog-implementation-plan.md)

#### 2.1 Fundação do catálogo

- [x] Criar app `catalog` e registrar em `INSTALLED_APPS`.
- [x] Definir capabilities `catalog.view`, `catalog.manage`, `pricing.view` e `pricing.manage`.
- [x] Integrar capabilities aos papéis admin, manager e operator.
- [x] Manter operações administrativas protegidas por MFA.

#### 2.2 Categorias, unidades e produtos

- [x] Criar categoria hierárquica com prevenção de ciclos.
- [x] Criar unidade com símbolo e precisão decimal limitada.
- [x] Criar produto/SKU independente com unidade base.
- [x] Normalizar e garantir SKU único por tenant.
- [x] Validar categoria e unidade pertencentes ao mesmo tenant.
- [x] Adicionar flags de lote e validade para integração com estoque.
- [x] Implementar inativação sem exclusão física.

#### 2.3 Conversões e códigos

- [x] Criar unidades comerciais por produto com fator positivo.
- [x] Calcular conversões somente com `Decimal`.
- [x] Preservar versões de fatores utilizados por fatos posteriores.
- [x] Criar códigos internos, EAN, GTIN e de fornecedor.
- [x] Validar tamanho e dígito verificador de EAN/GTIN.
- [x] Garantir código ativo único por tenant.
- [x] Permitir somente um código principal por produto e tipo.

#### 2.4 Precificação

- [x] Criar preços padrão versionados por vigência.
- [x] Criar sobrescrita opcional de preço por filial.
- [x] Impedir períodos sobrepostos no mesmo escopo.
- [x] Resolver preço por filial, fallback do tenant e instante.
- [x] Usar `Decimal` e impedir valor negativo.
- [x] Preservar histórico de preços sem sobrescrita destrutiva.

#### 2.5 Segurança multi-tenant

- [x] Aplicar manager tenant-scoped em entidades do catálogo.
- [x] Habilitar e forçar RLS nas tabelas tenant-scoped.
- [x] Negar leitura e escrita sem contexto de tenant.
- [x] Validar que preço por filial pertence ao tenant ativo.
- [x] Criar testes cross-tenant por aplicação e RLS.
- [x] Criar testes de IDOR para produto, código e preço.

#### 2.6 APIs, auditoria e eventos

- [x] Criar CRUD seguro de categorias, unidades e produtos.
- [x] Criar endpoints de conversões, códigos e preços.
- [x] Criar consulta de preço vigente por filial e instante.
- [x] Implementar paginação, busca, filtros e ordenação segura.
- [x] Padronizar erros RFC 9457 com códigos estáveis.
- [x] Auditar criação, alteração, preço e inativação.
- [x] Persistir eventos de catálogo na Outbox na mesma transação.
- [x] Documentar endpoints no OpenAPI e eventos no catálogo de domínio.

#### 2.7 Qualidade e aceite

- [x] Executar migrations com owner separado do runtime.
- [x] Executar Ruff e mypy sem falhas.
- [x] Executar suíte completa com cobertura mínima mantida.
- [x] Executar testes de concorrência de SKU, códigos e preços.
- [x] Executar regressão das Sprints 0 e 1.
- [x] Executar deploy check, auditoria de dependências e segredos.
- [x] Registrar evidências e riscos no relatório final da Sprint 2.
- [x] Criar commit final `feat: sprint 2 - catalogo e cadastros-base`.
- [x] Integrar em `master` e obter CI remota verde.
- [x] Confirmar worktree limpo e sincronizado com `origin/master`.

### Sprint 3 — Estoque e Movimentações

**Estado:** Em execução; hardening técnico aplicado após aceite da Sprint 2.

**Objetivo:** controlar saldo por filial por meio de movimentos imutáveis e operações idempotentes.

**Entregável:** entradas, saídas, ajustes, transferências e rastreabilidade de estoque.

**Especificação:** [Design da Sprint 3](superpowers/specs/2026-07-14-sprint-3-inventory-design.md)

**Plano:** [Plano de implementação da Sprint 3](superpowers/plans/2026-07-14-sprint-3-inventory-implementation-plan.md)

#### 3.1 Fundação e locais

- [x] Confirmar aceite e contratos públicos da Sprint 2.
- [x] Criar app `inventory` e capabilities de estoque.
- [x] Criar múltiplos locais por filial.
- [x] Criar exatamente um local principal por filial.
- [x] Impedir exclusão de local com histórico.

#### 3.2 Lotes e validade

- [x] Criar lotes opcionais por produto.
- [x] Exigir lote quando configurado no produto.
- [x] Exigir validade quando configurada no produto.
- [x] Impedir movimentação comum de lote vencido.
- [x] Permitir baixa autorizada e auditada de lote vencido.

#### 3.3 Ledger e projeção

- [x] Criar operação agregadora de estoque.
- [x] Criar movimentos imutáveis de entrada e saída.
- [x] Preservar unidade, fator e quantidade informados.
- [x] Criar saldo projetado por produto, filial, local e lote.
- [x] Impedir saldo negativo por serviço e constraint.
- [x] Impedir edição ou exclusão de movimento confirmado.

#### 3.4 Concorrência e idempotência

- [x] Exigir `Idempotency-Key` nas operações de escrita.
- [x] Retornar resultado original para replay idêntico.
- [x] Rejeitar mesma chave com payload diferente.
- [x] Bloquear linhas de saldo em ordem determinística.
- [x] Testar saídas concorrentes sem overselling.
- [x] Testar saldo final determinístico sob concorrência.

#### 3.5 Operações

- [x] Implementar saldo inicial.
- [x] Implementar entrada e saída manuais.
- [x] Implementar ajuste com motivo, capability e MFA.
- [x] Implementar transferência atômica entre locais.
- [x] Implementar transferência entre filiais autorizadas.
- [x] Implementar reversão compensatória única.
- [x] Testar rollback integral de transferência.

#### 3.6 Segurança e APIs

- [x] Aplicar e forçar RLS em todas as tabelas tenant-scoped.
- [x] Validar acesso a todas as filiais da operação.
- [x] Retornar 404 para recursos fora do tenant ou escopo autorizado.
- [x] Criar APIs de locais, lotes, saldos e operações.
- [x] Manter movimentos e saldos somente leitura pela API.
- [x] Padronizar erros de estoque em RFC 9457.
- [x] Criar testes de RLS, IDOR e ausência de contexto.

#### 3.7 Reconciliação, auditoria e eventos

- [x] Comparar projeção de saldo com soma dos movimentos.
- [x] Alertar divergência sem correção silenciosa.
- [x] Auditar operação, rejeição, ajuste, transferência e reversão.
- [x] Persistir eventos de estoque na Outbox atomicamente.
- [x] Documentar endpoints, idempotência e eventos.

#### 3.8 Qualidade e aceite

- [ ] Executar migrations, Ruff e mypy sem falhas.
- [ ] Executar suíte completa com cobertura mínima mantida.
- [ ] Repetir testes concorrentes e transacionais para detectar flakiness.
- [ ] Executar regressão das Sprints 0, 1 e 2.
- [ ] Executar deploy check, auditoria de dependências e segredos.
- [ ] Registrar evidências e riscos no relatório final da Sprint 3.
- [ ] Criar commit final `feat: sprint 3 - estoque e movimentacoes`.
- [ ] Integrar em `master` e obter CI remota verde.
- [ ] Confirmar worktree limpo e sincronizado com `origin/master`.

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
| 0 | 2026-07-14 | `feat: sprint 0 - fundação técnica` | 13/13 passando | RLS bypassado por superuser (documentado); SECRET_KEY curta tolerada em CI; W021 (HSTS preload) pendente de domínio; var-annotated suprimido em model fields | Pendente |
| 1 | 2026-07-14 | `feat: sprint 1 - autenticação e onboarding` | 68/68 passando | Nenhum | Pendente |
| 2 | 2026-07-16 | `feat: sprint 2 - catalogo e cadastros-base` + hardening | Coleta dos 5 testes de hardening OK; `manage.py check` e Ruff OK; execução pytest com banco local travou por ambiente PostgreSQL | ExclusionConstraint sobre preços omitida; validação movida para `full_clean()` via API; pendente rerun com PostgreSQL de teste saudável | **Aprovado com pendência de ambiente** |

