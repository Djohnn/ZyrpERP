# Sprint 1 Authentication, Onboarding and Authorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar cadastro público, ativação, sessões, MFA TOTP/e-mail, recuperação, convites e autorização por capability sem enfraquecer o isolamento multi-tenant da Sprint 0.

**Architecture:** O app `accounts` concentra credenciais, tokens temporários, MFA e sessões; `tenancy` concentra onboarding organizacional, política MFA, memberships, convites e capabilities. Views DRF delegam a serviços transacionais, artefatos temporários são persistidos somente como digest e todo acesso tenant-scoped mantém contexto PostgreSQL/RLS.

**Tech Stack:** Python 3.12+, Django 5.1, Django REST Framework, PostgreSQL 16, Redis, Celery, PyOTP, cryptography, django-ratelimit, pytest-django, Ruff e mypy.

---

### Task 1: Detalhar o PRD e preparar dependências/configuração

**Files:**
- Modify: `docs/PRD.md`
- Modify: `backend/pyproject.toml`
- Modify: `.env.example`
- Modify: `backend/config/settings/base.py`
- Modify: `backend/config/settings/local.py`
- Modify: `backend/config/settings/test.py`
- Modify: `backend/config/settings/production.py`

- [ ] **Step 1: Expandir a Sprint 1 no PRD**

Substituir a seção resumida por checklists para configuração, onboarding, sessão, MFA, recuperação, convites, capabilities, auditoria, testes e aceite. Todas as caixas começam abertas.

- [ ] **Step 2: Adicionar dependências**

Adicionar ao `pyproject.toml`:

```toml
"pyotp>=2.9,<3",
"cryptography>=44,<46",
"django-ratelimit>=4.1,<5",
```

- [ ] **Step 3: Configurar e-mail e criptografia por ambiente**

Adicionar settings `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`, SMTP, `MFA_ENCRYPTION_KEY`, expirações e limites. Produção exige a chave; testes usam chave Fernet descartável fixa e backend in-memory.

- [ ] **Step 4: Instalar e validar**

Run: `python -m pip install -e ".[dev]"`

Run: `python manage.py check --settings=config.settings.local`

Expected: instalação e check com exit code 0.

- [ ] **Step 5: Commit**

```bash
git add docs/PRD.md backend/pyproject.toml .env.example backend/config/settings
git commit -m "chore: prepare sprint 1 authentication"
```

### Task 2: Artefatos temporários e segurança criptográfica

**Files:**
- Create: `backend/accounts/security.py`
- Create: `backend/accounts/tokens.py`
- Modify: `backend/accounts/models.py`
- Create: `backend/accounts/migrations/0003_auth_security_models.py`
- Test: `backend/tests/test_auth_security.py`

- [ ] **Step 1: Escrever testes que falham**

Cobrir digest determinístico, comparação segura, token aleatório, expiração, consumo único, limite de tentativas e criptografia TOTP sem plaintext no banco.

```python
def test_one_time_token_cannot_be_consumed_twice(db):
    raw, record = issue_token(purpose='email_confirmation', user=user)
    assert consume_token(raw, purpose='email_confirmation').pk == record.pk
    assert consume_token(raw, purpose='email_confirmation') is None
```

- [ ] **Step 2: Confirmar RED**

Run: `pytest tests/test_auth_security.py -q -o addopts=''`

Expected: falha por módulos/modelos ausentes.

- [ ] **Step 3: Implementar modelos e helpers mínimos**

Criar `OneTimeToken` com `purpose`, `digest`, `user`, `expires_at`, `consumed_at`, `attempt_count` e timestamps; criar `MFADevice` com tipo, segredo cifrado, verificação e estado; criar `RecoveryCode` com digest e consumo. Usar HMAC-SHA256 para digests e Fernet para segredo TOTP.

- [ ] **Step 4: Gerar migration e confirmar GREEN**

Run: `python manage.py makemigrations accounts`

Run: `pytest tests/test_auth_security.py -q -o addopts=''`

Expected: todos aprovados.

- [ ] **Step 5: Commit**

```bash
git add backend/accounts backend/tests/test_auth_security.py
git commit -m "feat: add authentication security artifacts"
```

### Task 3: Onboarding público atômico e confirmação de e-mail

**Files:**
- Create: `backend/accounts/services/onboarding.py`
- Create: `backend/accounts/services/email_delivery.py`
- Create: `backend/accounts/serializers.py`
- Create: `backend/accounts/views/onboarding.py`
- Create: `backend/accounts/urls.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/outbox/handlers.py`
- Test: `backend/tests/test_onboarding_api.py`

- [ ] **Step 1: Escrever testes de API e rollback**

```python
def test_register_creates_complete_organization_atomically(api_client):
    response = api_client.post(reverse('accounts:register'), payload, format='json')
    assert response.status_code == 202
    user = User.objects.get(email='owner@example.test')
    membership = user.tenant_memberships.get(role='admin')
    assert Company.all_objects.filter(tenant=membership.tenant).count() == 1
    assert Branch.all_objects.filter(tenant=membership.tenant).count() == 1
```

Também provar e-mail duplicado com resposta genérica, slug collision, rollback forçado e Outbox sem token bruto.

- [ ] **Step 2: Confirmar RED**

Run: `pytest tests/test_onboarding_api.py -q -o addopts=''`

- [ ] **Step 3: Implementar serviço transacional**

`register_organization()` normaliza e-mail, cria usuário inativo operacionalmente, tenant, empresa, filial e membership admin em `transaction.atomic()`, emite token digest e agenda evento de e-mail com `transaction.on_commit`.

- [ ] **Step 4: Implementar confirmação**

`POST /api/v1/auth/email/confirm/` consome token válido, marca e-mail verificado e audita sem guardar token.

- [ ] **Step 5: Confirmar GREEN e regressão**

Run: `pytest tests/test_onboarding_api.py tests/test_isolation.py -q -o addopts=''`

- [ ] **Step 6: Commit**

```bash
git add backend/accounts backend/config/urls.py backend/outbox backend/tests/test_onboarding_api.py
git commit -m "feat: add public tenant onboarding"
```

### Task 4: Login, logout, identidade atual e rate limiting

**Files:**
- Create: `backend/accounts/services/sessions.py`
- Create: `backend/accounts/views/session.py`
- Modify: `backend/accounts/urls.py`
- Test: `backend/tests/test_session_auth.py`

- [ ] **Step 1: Escrever testes que falham**

Cobrir credencial válida, mensagem genérica para usuário/senha inválidos, e-mail não confirmado, conta inativa, rotação da chave de sessão, logout server-side, `/me/`, CSRF e rate limiting.

```python
def test_login_does_not_enumerate_accounts(client):
    missing = client.post(login_url, {'email': 'missing@example.test', 'password': 'wrong'})
    existing = client.post(login_url, {'email': user.email, 'password': 'wrong'})
    assert missing.status_code == existing.status_code == 401
    assert missing.json()['detail'] == existing.json()['detail']
```

- [ ] **Step 2: Confirmar RED**

Run: `pytest tests/test_session_auth.py -q -o addopts=''`

- [ ] **Step 3: Implementar sessão intermediária**

Login válido grava somente `pre_mfa_user_id` até o desafio MFA. Após MFA, usar `login()`, rotacionar sessão e gravar `mfa_verified_at`. Logout usa `django.contrib.auth.logout()`.

- [ ] **Step 4: Aplicar rate limiting**

Limitar login por IP sanitizado e e-mail normalizado, sem usar e-mail como label de log/métrica.

- [ ] **Step 5: Confirmar GREEN**

Run: `pytest tests/test_session_auth.py tests/test_observability.py -q -o addopts=''`

- [ ] **Step 6: Commit**

```bash
git add backend/accounts backend/tests/test_session_auth.py
git commit -m "feat: add secure session authentication"
```

### Task 5: Política MFA do tenant e TOTP

**Files:**
- Modify: `backend/tenancy/models.py`
- Create: `backend/tenancy/migrations/0004_mfa_policy.py`
- Create: `backend/tenancy/services/mfa_policy.py`
- Create: `backend/accounts/services/mfa.py`
- Create: `backend/accounts/views/mfa.py`
- Modify: `backend/accounts/urls.py`
- Test: `backend/tests/test_mfa_totp.py`
- Test: `backend/tests/test_mfa_policy_api.py`

- [ ] **Step 1: Escrever testes de política que falham**

Provar que ao menos um método fica permitido, somente `organization.manage` altera política, outro tenant recebe 404 e não se remove o único método verificado de um administrador.

- [ ] **Step 2: Escrever testes TOTP que falham**

Cobrir URI `otpauth`, segredo cifrado, ativação somente com código válido, replay bloqueado, janela limitada, remoção e auditoria sanitizada.

- [ ] **Step 3: Confirmar RED**

Run: `pytest tests/test_mfa_totp.py tests/test_mfa_policy_api.py -q -o addopts=''`

- [ ] **Step 4: Implementar política e enrollment**

Criar `TenantMFAPolicy` one-to-one. `begin_totp_enrollment()` gera segredo, persiste cifrado e retorna URI uma vez. `confirm_totp()` registra o último timestep aceito para impedir replay.

- [ ] **Step 5: Bloquear administrador sem MFA**

Adicionar permission DRF que exige `mfa_verified_at` na sessão para endpoints tenant-scoped administrativos.

- [ ] **Step 6: Confirmar GREEN e migrations**

Run: `pytest tests/test_mfa_totp.py tests/test_mfa_policy_api.py -q -o addopts=''`

Run: `python manage.py makemigrations --check --dry-run`

- [ ] **Step 7: Commit**

```bash
git add backend/accounts backend/tenancy backend/tests/test_mfa_*.py
git commit -m "feat: add tenant mfa policy and totp"
```

### Task 6: MFA por e-mail e códigos de recuperação

**Files:**
- Modify: `backend/accounts/services/mfa.py`
- Modify: `backend/accounts/views/mfa.py`
- Modify: `backend/accounts/urls.py`
- Test: `backend/tests/test_mfa_email.py`
- Test: `backend/tests/test_recovery_codes.py`

- [ ] **Step 1: Escrever testes que falham**

Cobrir expiração em dez minutos, cooldown, cinco tentativas, consumo único, ausência do código em logs/Outbox/auditoria e recuperação de uso único.

- [ ] **Step 2: Confirmar RED**

Run: `pytest tests/test_mfa_email.py tests/test_recovery_codes.py -q -o addopts=''`

- [ ] **Step 3: Implementar desafio por e-mail**

Gerar código com `secrets`, persistir digest e enviar somente após commit. Um sucesso consome o desafio, rotaciona a sessão e registra autenticação forte.

- [ ] **Step 4: Implementar recuperação**

Gerar códigos originais uma única vez, persistir hashes e invalidar o conjunto anterior na regeneração.

- [ ] **Step 5: Confirmar GREEN**

Run: `pytest tests/test_mfa_email.py tests/test_recovery_codes.py -q -o addopts=''`

- [ ] **Step 6: Commit**

```bash
git add backend/accounts backend/tests/test_mfa_email.py backend/tests/test_recovery_codes.py
git commit -m "feat: add email mfa and recovery codes"
```

### Task 7: Recuperação e troca de senha

**Files:**
- Create: `backend/accounts/services/passwords.py`
- Create: `backend/accounts/views/password.py`
- Modify: `backend/accounts/urls.py`
- Test: `backend/tests/test_password_recovery.py`

- [ ] **Step 1: Escrever testes que falham**

Provar resposta idêntica para e-mail existente/inexistente, token expirado/usado/adulterado, validação de senha Django, revogação de sessões e MFA obrigatório no login seguinte.

- [ ] **Step 2: Confirmar RED**

Run: `pytest tests/test_password_recovery.py -q -o addopts=''`

- [ ] **Step 3: Implementar forgot/reset**

Emitir token digest somente para usuário elegível, responder sempre 202, validar nova senha, consumir token e excluir todas as sessões associadas ao usuário.

- [ ] **Step 4: Confirmar GREEN**

Run: `pytest tests/test_password_recovery.py tests/test_session_auth.py -q -o addopts=''`

- [ ] **Step 5: Commit**

```bash
git add backend/accounts backend/tests/test_password_recovery.py
git commit -m "feat: add secure password recovery"
```

### Task 8: Capabilities, convites e gestão de memberships

**Files:**
- Create: `backend/tenancy/capabilities.py`
- Create: `backend/tenancy/services/authorization.py`
- Create: `backend/tenancy/services/invitations.py`
- Modify: `backend/tenancy/models.py`
- Create: `backend/tenancy/migrations/0005_invitations.py`
- Create: `backend/tenancy/serializers_access.py`
- Create: `backend/tenancy/views_access.py`
- Modify: `backend/tenancy/urls.py`
- Test: `backend/tests/test_capabilities.py`
- Test: `backend/tests/test_invitations_api.py`
- Test: `backend/tests/test_memberships_api.py`

- [ ] **Step 1: Escrever testes de capability que falham**

```python
@pytest.mark.parametrize(('role', 'capability', 'allowed'), [
    ('admin', 'users.manage', True),
    ('manager', 'users.manage', False),
    ('operator', 'organization.read', False),
])
def test_role_capability_matrix(role, capability, allowed):
    assert role_allows(role, capability) is allowed
```

- [ ] **Step 2: Escrever testes de convite/membership que falham**

Cobrir validade, uso único, reenvio, e-mail divergente, papel não escalável, filial de outro tenant, IDOR 404, remoção do último admin rejeitada e auditoria.

- [ ] **Step 3: Confirmar RED**

Run: `pytest tests/test_capabilities.py tests/test_invitations_api.py tests/test_memberships_api.py -q -o addopts=''`

- [ ] **Step 4: Implementar matriz e autorização contextual**

Centralizar papéis/capabilities em constantes imutáveis e `authorize(user, tenant, capability, branch=None)`. Nenhuma view compara papel diretamente.

- [ ] **Step 5: Implementar convites e memberships**

Persistir `Invitation` com digest, e-mail normalizado, papel, expiração, aceite e filiais do mesmo tenant. Atualizações de membership validam capability e invariantes administrativas.

- [ ] **Step 6: Confirmar GREEN e IDOR**

Run: `pytest tests/test_capabilities.py tests/test_invitations_api.py tests/test_memberships_api.py tests/test_isolation.py -q -o addopts=''`

- [ ] **Step 7: Commit**

```bash
git add backend/tenancy backend/tests/test_capabilities.py backend/tests/test_invitations_api.py backend/tests/test_memberships_api.py
git commit -m "feat: add capabilities invitations and memberships"
```

### Task 9: Auditoria, documentação e contratos

**Files:**
- Modify: `backend/audit/services.py`
- Modify: `backend/tests/test_audit.py`
- Modify: `docs/05_API/openapi.yaml`
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `.secrets.baseline`

- [ ] **Step 1: Escrever testes de sanitização que falham**

Adicionar estruturas aninhadas com `otp`, `mfa_code`, `recovery_code`, `totp_secret`, `invitation_token` e `reset_token`; todas devem virar `[REDACTED]`.

- [ ] **Step 2: Confirmar RED e implementar redaction**

Run: `pytest tests/test_audit.py -q -o addopts=''`

Atualizar chaves sensíveis e repetir até GREEN.

- [ ] **Step 3: Atualizar OpenAPI e READMEs**

Documentar endpoints, estados 202/401/403/404/409/429, cookies/CSRF, SMTP, chave MFA e fluxo local sem incluir credenciais reais.

- [ ] **Step 4: Atualizar baseline de segredos**

Executar scanner, revisar somente nomes/tipos e normalizar caminhos para CI Linux. O baseline não armazena valores originais.

- [ ] **Step 5: Commit**

```bash
git add backend/audit backend/tests/test_audit.py docs/05_API/openapi.yaml README.md backend/README.md .secrets.baseline
git commit -m "docs: document sprint 1 security contracts"
```

### Task 10: Gate final, PRD e entrega

**Files:**
- Modify: `docs/PRD.md`
- Modify: `docs/CHANGELOG.md`
- Create: `docs/10_Releases/SPRINT-001_Auth_Onboarding_Final_Report.md`
- Modify: `docs/10_Releases/MILESTONE-001_MANIFEST.txt`

- [ ] **Step 1: Aplicar migrations com owner**

Run: `python manage.py migrate --settings=config.settings.migration`

Run: `python manage.py migrate --check --settings=config.settings.migration`

- [ ] **Step 2: Executar gate completo local**

```bash
python manage.py check --settings=config.settings.local
python manage.py makemigrations --check --dry-run --settings=config.settings.migration
ruff check .
mypy .
pytest
python manage.py check --deploy --settings=config.settings.production
```

Expected: zero falhas, cobertura mínima mantida e nenhuma regressão da Sprint 0.

- [ ] **Step 3: Executar revisão de segurança**

Confirmar runtime sem `SUPERUSER/BYPASSRLS`, portas locais em `127.0.0.1`, hook de segredos aprovado e ausência de tokens/códigos/senhas em diff, logs e auditoria.

- [ ] **Step 4: Atualizar PRD por evidência**

Marcar `[x]` somente depois do comando correspondente. Registrar contagem real de testes, cobertura, migrations, limitações e CI no relatório.

- [ ] **Step 5: Atualizar changelog e manifesto**

Regenerar hashes SHA-256 de todos os documentos, excluindo o próprio manifesto e ZIPs.

- [ ] **Step 6: Commit final e push**

```bash
git add .
git commit -m "feat: sprint 1 - autenticação e onboarding"
git push origin master
```

- [ ] **Step 7: Validar CI remota**

Consultar o run do commit final e corrigir qualquer gate até obter `completed success`. Confirmar `git status --short` vazio e `HEAD == origin/master`.
