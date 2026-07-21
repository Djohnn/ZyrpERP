# Sprint 17 — Shell Administrativo, Tenancy e Acessos — Design

## Objetivo

Entregar o primeiro painel web utilizável para administração de tenant, empresas, filiais, membros, convites, dispositivos e políticas de segurança.

## Escopo

Evoluir o shell da Sprint 16 com navegação baseada em capacidades, contexto de empresa/filial, administração de acessos e estados responsivos de carregamento, vazio e erro.

## Componentes

- Layout autenticado com menu, cabeçalho, breadcrumbs e seletor de tenant/filial.
- Dashboard inicial com atalhos autorizados e saúde resumida.
- Perfil e sessão do usuário.
- CRUD de empresas e filiais.
- Membros, convites, papéis e escopo por filial.
- Política MFA e dispositivos PDV cadastrados.

## Autorização

- Menu e ações usam capacidades do backend, mas o backend permanece autoridade final.
- Acesso de outro tenant deve resultar em 404 sem revelar existência.
- Operações administrativas sensíveis exigem MFA conforme política atual.
- Troca de tenant/filial reinicia queries e formulários pendentes.

## Experiência de uso

- Tabelas com paginação, busca e filtros persistidos na URL.
- Formulários com validação de campo e resumo de erro.
- Confirmação explícita para revogação, desativação e alterações de política.
- Interface responsiva para desktop e tablet; operação em celular é consulta assistida.

## Testes

- Componentes e hooks com Testing Library/MSW.
- Testes API de permissões, paginação e isolamento que faltarem.
- Playwright para convite, troca de filial e revogação de dispositivo.
- axe-core em navegação, tabelas, dialogs e formulários.

## Fora do escopo

- Administração global SaaS da Sprint 15.
- Impersonação permanente de usuário.
- Telas de catálogo, estoque ou vendas.

## Critérios de aceite

- Administrador gerencia empresas, filiais, membros e convites.
- Operador enxerga apenas navegação e ações autorizadas.
- Dispositivo PDV pode ser consultado e revogado com auditoria.
- URLs são compartilháveis sem incluir segredo ou estado sensível.
- Fluxos críticos passam em Chromium, Firefox e WebKit.
