# SEC-001 — Security and Multi-Tenancy

| Campo | Valor |
|---|---|
| Código | SEC-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Dependências | ADR-002, SAD-001 |
| Última atualização | 2026-07-14 |

## Isolamento
Tenant é resolvido após autenticação e passado explicitamente ao caso de uso. QuerySets, constraints e PostgreSQL RLS aplicam deny-by-default. Contexto acompanha Celery, Outbox, Redis, object storage, auditoria e exportações.

## Identidade e autorização
Usuário global possui memberships. Permissões combinam tenant, empresa, filial, papel e ação. MFA é obrigatório para administradores e funções fiscais/financeiras sensíveis. Dispositivo PDV tem credencial própria, curta e revogável.

## Segredos e criptografia
TLS em trânsito; storage e backups criptografados. Tokens, senha de certificado e material A1 são Restricted, protegidos por envelope encryption/secrets manager. Nenhum segredo aparece em logs, eventos ou SQLite quando evitável.

## Aplicação
Proteções contra IDOR, CSRF, XSS, SSRF, injection, brute force e webhook replay. Inputs têm schema e limites. URLs assinadas expiram. Operações críticas exigem idempotência e auditoria.

## LGPD
Inventário de dados, finalidade, base legal, minimização, retenção, exportação, correção e exclusão compatível com obrigações fiscais. Solicitações são autenticadas e auditadas.

## Verificação
Testes com dois tenants cobrem API, ORM, RLS, jobs, cache, arquivos e eventos. Backups passam por restauração. Scanners de segredo, dependência e SAST integram CI.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Controles iniciais. |

