# Sprint 1 — Relatório Final de Autenticação e Onboarding

Data: 2026-07-14  
Estado: validação local concluída; CI remota pendente

## Resultado

A Sprint 1 entrega onboarding transacional do primeiro administrador, confirmação de
e-mail, autenticação por sessão, MFA por TOTP ou e-mail, códigos de recuperação,
recuperação de senha, capabilities, convites e gestão de memberships por tenant e filial.

## Evidências locais

- PostgreSQL 16 e Redis 7 saudáveis, publicados somente em `127.0.0.1`;
- migrations sem alterações ou aplicações pendentes;
- `manage.py check` e `check --deploy` sem problemas;
- Ruff aprovado e mypy aprovado em 91 arquivos;
- 68 testes aprovados com PostgreSQL real e cobertura superior ao mínimo de 80%;
- testes de RLS, IDOR, ausência de contexto e papéis não privilegiados sem regressão;
- onboarding integralmente revertido quando uma etapa falha;
- tokens de confirmação, recuperação, convite e MFA expirados, limitados e de uso único;
- segredo TOTP cifrado e códigos de recuperação armazenados somente como digest;
- login protegido por CSRF, estado pré-MFA e rotação da sessão após elevação;
- redefinição de senha invalida sessões existentes e preserva a exigência de MFA;
- filial de outro tenant é rejeitada antes de qualquer atualização de membership;
- hook de segredos aprovado com baseline revisado.

## Segurança de dados

Nenhum token, código MFA, segredo TOTP, senha ou credencial real foi incluído no
repositório, logs, auditoria ou Outbox. A chave Fernet é externa por ambiente e o CI gera
uma chave efêmera durante cada execução.

## Riscos residuais

- A auditoria local de dependências foi bloqueada pela cadeia TLS da máquina; o
  `pip-audit --strict` permanece obrigatório no GitHub Actions.
- E-mail de produção depende de SMTP configurado pelo operador e precisa de teste de
  entrega no ambiente de homologação.
- O frontend de onboarding e as telas MFA pertencem a uma sprint posterior; esta entrega
  estabelece os contratos e fluxos seguros do backend.
- Operações fiscais, PDV e IA continuam fora do escopo desta sprint.

## Encerramento

O aceite definitivo depende do commit final, integração em `master`, CI remota verde e
confirmação do worktree limpo e sincronizado.
