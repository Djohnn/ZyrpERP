# EH-001 — Engineering Handbook

| Campo | Valor |
|---|---|
| Código | EH-001 |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Engineering Lead |
| Aprovador | Architecture Owner |
| Última atualização | 2026-07-14 |
| Dependências | SAD-001, PG-001 |
| Documentos relacionados | TST-001, SEC-001, API-001 |

## 1. Python e Django
Python tipado, formatação e lint automatizados. Custom user model no primeiro migration. Settings por ambiente e segredos fora do repositório. Views, serializers, signals e models não concentram casos de uso.

## 2. Módulos
Imports seguem direção `interfaces → application → domain`; infrastructure implementa ports. Acesso ao modelo de outro módulo ocorre por serviço público ou contrato documentado.

## 3. Transações
Casos de uso definem limites atômicos. Side effects externos não ocorrem dentro da transação; registram Outbox. Locks são específicos e curtos.

## 4. Dinheiro e tempo
`Decimal`, moeda explícita e política de arredondamento documentada. UTC em persistência; fuso da empresa em regras de calendário. Nunca usar `float` para valor financeiro.

## 5. Banco e migrations
Migration pequena, reversível quando possível e compatível com deploy gradual. Constraints protegem invariantes locais. QuerySets são avaliados com `select_related`, `prefetch_related` e planos de consulta.

## 6. APIs e eventos
OpenAPI, Problem Details, idempotência, versionamento e paginação uniforme. Evento é fato passado, imutável e versionado; payload contém tenant e correlation ID sem segredos.

## 7. Logging
Logs estruturados, sem PII desnecessária, tokens, certificados ou senhas. Exceções preservam correlation ID. Auditoria de negócio é registro separado.

## 8. Testes
TDD para regras e correções. Testes de isolamento usam dois tenants. Integração roda com PostgreSQL real quando valida RLS/transação. Mocks ficam nas fronteiras externas.

## 9. Revisão e Git
Commits pequenos em Conventional Commits. Review verifica domínio, segurança, queries, migração, testes, observabilidade e documentação. Branch não integra com checks falhando.

## 10. Dependências
Nova dependência exige justificativa, licença compatível, manutenção ativa e análise de vulnerabilidade. Framework externo não entra no domínio.

## 11. Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Práticas iniciais. |
