# API-001 — API Standards

| Campo | Valor |
|---|---|
| Código | API-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | SAD-001, SEC-001 |
| Última atualização | 2026-07-14 |

## Contratos
- Base path `/api/v1`; HTTPS obrigatório fora de local.
- JSON UTF-8 e OpenAPI como contrato verificável.
- Autenticação por sessão segura no Web e tokens curtos para clientes autorizados.
- Tenant deriva da associação autenticada; IDs enviados pelo cliente não concedem acesso.
- `X-Correlation-ID` é aceito ou criado e propagado.
- `Idempotency-Key` é obrigatório em criação de venda, pagamento, sincronização e fiscal.
- Dinheiro é string decimal acompanhado de moeda; datas seguem ISO 8601.
- Paginação por cursor para coleções mutáveis; filtros e ordenação são allowlist.
- Concorrência usa `ETag`/`If-Match` ou campo `version` em recursos editáveis.
- Erros seguem `application/problem+json` e catálogo estável.

## Problem Details
Campos: `type`, `title`, `status`, `detail`, `instance`, `code`, `correlation_id` e `errors` para validação. Mensagem não expõe stack, segredo ou existência de recurso cross-tenant.

## Compatibilidade
Mudança aditiva permanece em v1. Remoção, mudança semântica ou tipo incompatível exige nova versão e janela de depreciação. Campos desconhecidos em resposta devem ser tolerados.

## Segurança e limites
Rate limit por tenant, usuário, dispositivo e operação. Logs registram metadados, nunca payload sensível integral. Downloads usam autorização e URL temporária curta.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Padrões iniciais. |

