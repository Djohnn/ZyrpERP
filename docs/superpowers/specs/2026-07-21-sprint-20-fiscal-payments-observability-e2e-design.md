# Sprint 20 — Fiscal, Pagamentos, Observabilidade e Aceite E2E — Design

## Objetivo

Completar o painel web com operação fiscal, pagamentos integrados, observabilidade e uma suíte E2E que valide o produto administrativo de ponta a ponta.

## Fiscal

- Configuração de emitente e produtos fiscais.
- Acompanhamento de documentos, status, rejeições, retries e cancelamentos.
- Consulta segura de XML/PDF quando autorizada.
- Reconciliação de entrada fiscal com compras/recebimentos.

## Pagamentos

- Configuração de provider sem revelar segredo após gravação.
- Intenções e transações por venda.
- Lotes de conciliação, taxas, valores líquidos e divergências.
- Confirmação de lote somente sem pendência de revisão.

## Observabilidade

- Saúde, readiness e métricas operacionais autorizadas.
- Indicadores de filas, Outbox, documentos fiscais e webhooks.
- Correlation ID navegável entre erro de interface e diagnóstico.
- Runbooks relacionados a alertas, sem expor credenciais.

## Aceite E2E

Jornadas Playwright cobrirão:

1. login, MFA, tenant e filial;
2. catálogo, estoque e compra com recebimento;
3. consulta de venda criada pelo seed/PDV e correção autorizada;
4. pessoa, financeiro e relatório;
5. fiscal e conciliação de pagamento;
6. bloqueios por papel e cross-tenant;
7. expiração de sessão, erro de rede e recuperação.

## Qualidade de release

- Build reproduzível e bundle analisado.
- Testes Chromium, Firefox e WebKit.
- Auditoria axe-core sem violações críticas/sérias nos fluxos cobertos.
- Contrato OpenAPI sem drift e smoke pós-deploy.
- Evidências estruturadas em JUnit/HTML no CI.

## Fora do escopo

- Provider real obrigatório.
- Homologação TEF.
- Copiloto com permissão de escrita.
- Aplicativo móvel nativo.

## Critérios de aceite

- Gestor opera todos os módulos web previstos sem acesso direto ao Django Admin.
- Segredos fiscais e de pagamento nunca retornam ao frontend.
- Falhas críticas apresentam correlation ID e orientação acionável.
- Jornada administrativa completa passa nos três engines do Playwright.
- Backend e frontend possuem gates de contrato, segurança, acessibilidade e regressão.
