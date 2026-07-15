# Sprint 3 Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar estoque por filial e local com lotes opcionais, movimentos imutáveis, transferências atômicas, idempotência e bloqueio de saldo negativo.

**Architecture:** Criar o bounded context `inventory` após o aceite da Sprint 2. Serviços transacionais bloqueiam projeções `StockBalance`, persistem fatos imutáveis `StockMovement` e gravam auditoria/Outbox na mesma transação; RLS e escopo de filial protegem todas as dimensões.

**Tech Stack:** Python 3.12+, Django 5.1, Django REST Framework, PostgreSQL 16, pytest-django, transações e row locks PostgreSQL.

---

### Task 1: Scaffold, capabilities e local principal

**Files:**
- Create: `backend/inventory/__init__.py`
- Create: `backend/inventory/apps.py`
- Create: `backend/inventory/models.py`
- Create: `backend/inventory/migrations/0001_initial.py`
- Modify: `backend/config/settings/base.py`
- Modify: `backend/tenancy/capabilities.py`
- Test: `backend/tests/test_stock_locations.py`

- [ ] **Step 1: Escrever testes do local principal**

```python
@pytest.mark.django_db
def test_branch_has_exactly_one_primary_stock_location(branch):
    location = ensure_primary_location(branch=branch)
    repeated = ensure_primary_location(branch=branch)
    assert repeated.pk == location.pk
    assert StockLocation.all_objects.filter(branch=branch, is_primary=True).count() == 1
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_stock_locations.py -q -o addopts=''`

Expected: FAIL por app ausente.

- [ ] **Step 3: Implementar `StockLocation` e capabilities**

```python
class StockLocation(TimeStampedModel, TenantScopedModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    location_type = models.CharField(max_length=20, default='general')
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

Adicionar unicidade `(tenant, branch, code)` e constraint condicional para um principal
por filial. Ampliar matriz com `inventory.view/receive/issue/transfer/adjust` e
`inventory.locations.manage` conforme a especificação.

- [ ] **Step 4: Migrar e testar**

Run: `cd backend && python manage.py makemigrations inventory && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_stock_locations.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/inventory backend/config/settings/base.py backend/tenancy/capabilities.py backend/tests/test_stock_locations.py
git commit -m "feat(inventory): add stock locations"
```

### Task 2: Lotes e validade opcionais

**Files:**
- Modify: `backend/inventory/models.py`
- Create: `backend/inventory/services/lots.py`
- Create: `backend/inventory/migrations/0002_stocklot.py`
- Test: `backend/tests/test_stock_lots.py`

- [ ] **Step 1: Escrever testes de obrigatoriedade**

```python
def test_product_requiring_lot_rejects_missing_lot(lot_required_product):
    with pytest.raises(LotRequired):
        validate_lot(product=lot_required_product, lot=None, movement_type='receipt')


def test_expired_lot_allows_only_authorized_disposal(expired_lot):
    with pytest.raises(ExpiredLot):
        validate_lot(product=expired_lot.product, lot=expired_lot, movement_type='issue')
    validate_lot(product=expired_lot.product, lot=expired_lot, movement_type='disposal')
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_stock_lots.py -q -o addopts=''`

Expected: FAIL.

- [ ] **Step 3: Implementar `StockLot` e validação**

```python
class StockLot(TimeStampedModel, TenantScopedModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    number = models.CharField(max_length=80)
    manufactured_at = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

Validar mesmo tenant, unicidade `(tenant, product, number)`, ordem das datas e flags
`requires_lot/requires_expiry` do catálogo.

- [ ] **Step 4: Migrar e testar**

Run: `cd backend && python manage.py makemigrations inventory && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_stock_lots.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/inventory backend/tests/test_stock_lots.py
git commit -m "feat(inventory): add optional lot tracking"
```

### Task 3: Operações, movimentos imutáveis e saldo

**Files:**
- Modify: `backend/inventory/models.py`
- Create: `backend/inventory/services/movements.py`
- Create: `backend/inventory/migrations/0003_stock_core.py`
- Test: `backend/tests/test_stock_movements.py`

- [ ] **Step 1: Escrever testes de imutabilidade e projeção**

```python
@pytest.mark.django_db(transaction=True)
def test_receipt_creates_movement_and_balance(stock_context):
    operation = receive_stock(**stock_context, quantity=Decimal('20.000'))
    assert operation.movements.count() == 1
    assert StockBalance.objects.get(product=stock_context['product']).quantity == Decimal('20.000')


@pytest.mark.django_db
def test_confirmed_movement_is_immutable(confirmed_movement):
    confirmed_movement.base_quantity = Decimal('999')
    with pytest.raises(ImmutableStockMovement):
        confirmed_movement.save()
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_stock_movements.py -q -o addopts=''`

Expected: FAIL.

- [ ] **Step 3: Implementar models**

`StockOperation` contém tipo, estado, chave idempotente, digest do payload, motivo e ator.
`StockMovement` contém operação, produto, filial, local, lote, direção, quantidade base,
unidade comercial, quantidade informada e fator aplicado. `StockBalance` contém as mesmas
dimensões e quantidade com constraint `quantity >= 0`.

- [ ] **Step 4: Implementar serviço transacional**

```python
@transaction.atomic
def apply_movement(*, operation, product, branch, location, lot, direction, base_quantity):
    balance, _ = StockBalance.objects.select_for_update().get_or_create(
        tenant=operation.tenant, product=product, branch=branch, location=location, lot=lot,
        defaults={'quantity': Decimal('0')},
    )
    delta = base_quantity if direction == 'in' else -base_quantity
    if balance.quantity + delta < 0:
        raise InsufficientStock(balance.quantity, base_quantity)
    movement = StockMovement.objects.create(
        tenant=operation.tenant,
        operation=operation,
        product=product,
        branch=branch,
        location=location,
        lot=lot,
        direction=direction,
        base_quantity=base_quantity,
        commercial_unit=product.base_unit,
        commercial_quantity=base_quantity,
        conversion_factor=Decimal('1'),
    )
    balance.quantity = F('quantity') + delta
    balance.save(update_fields=['quantity', 'updated_at'])
    return movement
```

- [ ] **Step 5: Migrar e testar**

Run: `cd backend && python manage.py makemigrations inventory && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_stock_movements.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/inventory backend/tests/test_stock_movements.py
git commit -m "feat(inventory): add immutable stock ledger"
```

### Task 4: Idempotência e saldo não negativo sob concorrência

**Files:**
- Create: `backend/inventory/services/idempotency.py`
- Modify: `backend/inventory/services/movements.py`
- Test: `backend/tests/test_stock_idempotency.py`
- Test: `backend/tests/test_stock_concurrency.py`

- [ ] **Step 1: Escrever testes de replay e conflito**

```python
@pytest.mark.django_db(transaction=True)
def test_same_idempotency_key_returns_original_operation(receipt_payload):
    first = receive_stock(**receipt_payload, idempotency_key='receipt-001')
    replay = receive_stock(**receipt_payload, idempotency_key='receipt-001')
    assert replay.pk == first.pk


@pytest.mark.django_db(transaction=True)
def test_same_key_with_different_payload_is_rejected(receipt_payload):
    receive_stock(**receipt_payload, idempotency_key='receipt-002')
    with pytest.raises(IdempotencyConflict):
        receive_stock(**receipt_payload, quantity=Decimal('2'), idempotency_key='receipt-002')
```

- [ ] **Step 2: Escrever teste concorrente**

Criar saldo 10 e disparar duas transações em conexões/threads independentes tentando
retirar 7. Exigir uma confirmação, uma `InsufficientStock` e saldo final 3.

- [ ] **Step 3: Confirmar falhas iniciais**

Run: `cd backend && python -m pytest tests/test_stock_idempotency.py tests/test_stock_concurrency.py -q -o addopts=''`

Expected: FAIL.

- [ ] **Step 4: Implementar digest e locks ordenados**

Canonicalizar JSON, calcular SHA-256, bloquear operação pela chave `(tenant, key)` e
ordenar dimensões de saldo por UUID antes de `select_for_update`. Nunca repetir operação
sem a mesma chave.

- [ ] **Step 5: Rodar testes cinco vezes**

Run: `cd backend && 1..5 | % { python -m pytest tests/test_stock_idempotency.py tests/test_stock_concurrency.py -q -o addopts='' }`

Expected: cinco execuções PASS sem flakiness.

- [ ] **Step 6: Commit**

```bash
git add backend/inventory backend/tests/test_stock_idempotency.py backend/tests/test_stock_concurrency.py
git commit -m "feat(inventory): enforce idempotent stock updates"
```

### Task 5: Transferências e reversões compensatórias

**Files:**
- Create: `backend/inventory/services/transfers.py`
- Create: `backend/inventory/services/reversals.py`
- Test: `backend/tests/test_stock_transfers.py`
- Test: `backend/tests/test_stock_reversals.py`

- [ ] **Step 1: Escrever teste de transferência atômica**

```python
@pytest.mark.django_db(transaction=True)
def test_transfer_moves_stock_atomically(source_balance, target_location):
    operation = transfer_stock(
        source=source_balance.location, target=target_location,
        product=source_balance.product, quantity=Decimal('4'),
        idempotency_key='transfer-001', actor=actor,
    )
    assert list(operation.movements.values_list('direction', flat=True)) == ['out', 'in']
    assert balance(source_balance.location) == Decimal('6')
    assert balance(target_location) == Decimal('4')
```

- [ ] **Step 2: Escrever testes de rollback e reversão única**

Forçar falha ao criar a entrada e provar que saída/saldo não mudaram. Reverter operação,
provar movimentos compensatórios e rejeitar segunda reversão.

- [ ] **Step 3: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_stock_transfers.py tests/test_stock_reversals.py -q -o addopts=''`

Expected: FAIL.

- [ ] **Step 4: Implementar serviços**

Transferência cria uma operação e dois movimentos dentro de uma transação. Reversão
carrega movimentos originais, inverte direções, preserva dimensões, referencia
`reverses_operation` e bloqueia dupla reversão com constraint única.

- [ ] **Step 5: Rodar testes**

Run: `cd backend && python -m pytest tests/test_stock_transfers.py tests/test_stock_reversals.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/inventory backend/tests/test_stock_transfers.py backend/tests/test_stock_reversals.py
git commit -m "feat(inventory): add transfers and reversals"
```

### Task 6: RLS, filial e APIs de estoque

**Files:**
- Create: `backend/inventory/migrations/0004_inventory_rls.py`
- Create: `backend/inventory/serializers.py`
- Create: `backend/inventory/permissions.py`
- Create: `backend/inventory/views.py`
- Create: `backend/inventory/urls.py`
- Modify: `backend/config/urls.py`
- Test: `backend/tests/test_inventory_api.py`
- Test: `backend/tests/test_inventory_isolation.py`

- [ ] **Step 1: Escrever testes de API e isolamento**

```python
@pytest.mark.django_db
def test_issue_requires_idempotency_key(authenticated_inventory_client, stock_payload):
    response = authenticated_inventory_client.post('/api/v1/stock-operations/issues/', stock_payload, format='json')
    assert response.status_code == 400
    assert response.json()['code'] == 'idempotency_key_required'


@pytest.mark.django_db
def test_transfer_requires_access_to_both_branches(client_with_one_branch, transfer_payload):
    response = client_with_one_branch.post(
        '/api/v1/stock-operations/transfers/', transfer_payload,
        format='json', HTTP_IDEMPOTENCY_KEY='branch-denied-001',
    )
    assert response.status_code == 404
```

- [ ] **Step 2: Confirmar falhas iniciais**

Run: `cd backend && python -m pytest tests/test_inventory_api.py tests/test_inventory_isolation.py -q -o addopts=''`

Expected: FAIL com rotas ausentes.

- [ ] **Step 3: Aplicar RLS e APIs**

Forçar RLS em locations, lots, operations, movements e balances. Criar endpoints da
especificação; movimentos e saldos são somente leitura. Validar capability, MFA para
ajustes/administração, tenant, filial e `Idempotency-Key` antes do serviço.

- [ ] **Step 4: Padronizar erros**

Mapear exceções de domínio para RFC 9457 com códigos `insufficient_stock`, `lot_required`,
`expired_lot`, `idempotency_conflict`, `operation_already_reversed`,
`branch_access_denied` e `stock_movement_immutable`.

- [ ] **Step 5: Rodar testes**

Run: `cd backend && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_inventory_api.py tests/test_inventory_isolation.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/inventory backend/config/urls.py backend/tests/test_inventory_api.py backend/tests/test_inventory_isolation.py
git commit -m "feat(inventory): expose tenant-safe stock APIs"
```

### Task 7: Reconciliação, auditoria e Outbox

**Files:**
- Create: `backend/inventory/services/reconciliation.py`
- Create: `backend/inventory/services/events.py`
- Create: `backend/inventory/management/commands/reconcile_stock.py`
- Modify: `docs/03_Domain/DOMAIN_EVENT_CATALOG.md`
- Modify: `docs/05_API/openapi.yaml`
- Test: `backend/tests/test_stock_reconciliation.py`
- Test: `backend/tests/test_inventory_observability.py`

- [ ] **Step 1: Escrever teste de divergência**

```python
@pytest.mark.django_db
def test_reconciliation_reports_but_does_not_silently_fix_divergence(stock_balance):
    StockBalance.objects.filter(pk=stock_balance.pk).update(quantity=Decimal('999'))
    findings = reconcile_stock(tenant=stock_balance.tenant)
    stock_balance.refresh_from_db()
    assert findings[0].balance_id == stock_balance.id
    assert stock_balance.quantity == Decimal('999')
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_stock_reconciliation.py tests/test_inventory_observability.py -q -o addopts=''`

Expected: FAIL.

- [ ] **Step 3: Implementar reconciliação e eventos**

Somar movimentos por dimensões, comparar projeção, emitir log/métrica sanitizada e retornar
achados. Persistir auditoria e Outbox na transação de cada operação com eventos versionados
`inventory.stock.changed.v1`, `inventory.transfer.completed.v1`,
`inventory.adjustment.completed.v1` e `inventory.operation.reversed.v1`.

- [ ] **Step 4: Documentar API e catálogo de eventos**

Adicionar schemas, erros, idempotência, filtros e payload mínimo de eventos.

- [ ] **Step 5: Rodar testes**

Run: `cd backend && python -m pytest tests/test_stock_reconciliation.py tests/test_inventory_observability.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/inventory docs/03_Domain/DOMAIN_EVENT_CATALOG.md docs/05_API/openapi.yaml backend/tests/test_stock_reconciliation.py backend/tests/test_inventory_observability.py
git commit -m "feat(inventory): reconcile and audit stock ledger"
```

### Task 8: Gate e encerramento da Sprint 3

**Files:**
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-003_Inventory_Final_Report.md`
- Modify: `docs/10_Releases/MILESTONE-001_MANIFEST.txt`

- [ ] **Step 1: Rodar gate completo**

Run:

```bash
cd backend
python manage.py makemigrations --check --dry-run --settings=config.settings.migration
python manage.py migrate --check --settings=config.settings.migration
ruff check .
mypy .
python -m pytest -q
python manage.py check --deploy --settings=config.settings.production
```

Expected: zero falhas e cobertura mínima mantida.

- [ ] **Step 2: Repetir testes críticos**

Run: `cd backend && 1..10 | % { python -m pytest tests/test_stock_concurrency.py tests/test_stock_transfers.py tests/test_stock_idempotency.py -q -o addopts='' }`

Expected: dez execuções PASS.

- [ ] **Step 3: Auditar dependências e segredos**

Run: `cd backend && python -m pip freeze --exclude-editable > requirements-audit.txt && pip-audit --strict --requirement requirements-audit.txt`

Run: `git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline`

Expected: zero vulnerabilidades e nenhum segredo novo.

- [ ] **Step 4: Atualizar documentação, relatório e manifesto**

Registrar evidências, concorrência, RLS, riscos e somente marcar tarefas comprovadas.
Regenerar o manifesto documental determinístico.

- [ ] **Step 5: Commit final**

```bash
git add README.md backend/README.md docs
git commit -m "feat: sprint 3 - estoque e movimentacoes"
```

- [ ] **Step 6: Integrar e validar CI**

Enviar para `master`, acompanhar GitHub Actions até verde, remover o worktree somente após
integração comprovada e confirmar `master == origin/master` com árvore limpa.
