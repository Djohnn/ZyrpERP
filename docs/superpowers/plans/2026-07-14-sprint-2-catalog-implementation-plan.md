# Sprint 2 Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar catálogo multi-tenant com categorias, unidades, SKUs, conversões, códigos e preços vigentes por tenant ou filial.

**Architecture:** Criar o bounded context Django `catalog`, isolado por tenant e protegido por RLS. Serviços de domínio concentram normalização, conversão e resolução de preço; APIs DRF usam capabilities existentes, auditoria e Transactional Outbox.

**Tech Stack:** Python 3.12+, Django 5.1, Django REST Framework, PostgreSQL 16, pytest-django, Ruff, mypy.

---

### Task 1: Scaffold do app e capabilities

**Files:**
- Create: `backend/catalog/__init__.py`
- Create: `backend/catalog/apps.py`
- Create: `backend/catalog/capabilities.py`
- Create: `backend/catalog/migrations/__init__.py`
- Modify: `backend/config/settings/base.py`
- Modify: `backend/tenancy/capabilities.py`
- Test: `backend/tests/test_catalog_capabilities.py`

- [ ] **Step 1: Escrever o teste de capabilities**

```python
import pytest

from tenancy.capabilities import role_allows


@pytest.mark.parametrize(
    ('role', 'capability', 'allowed'),
    [
        ('admin', 'catalog.manage', True),
        ('manager', 'catalog.manage', True),
        ('operator', 'catalog.manage', False),
        ('operator', 'catalog.view', True),
        ('operator', 'pricing.view', True),
        ('operator', 'pricing.manage', False),
    ],
)
def test_catalog_capability_matrix(role, capability, allowed):
    assert role_allows(role, capability) is allowed
```

- [ ] **Step 2: Confirmar a falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_capabilities.py -q -o addopts=''`

Expected: FAIL porque as capabilities ainda não existem.

- [ ] **Step 3: Criar o app e ampliar a matriz**

```python
# catalog/apps.py
from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
```

Adicionar `catalog.apps.CatalogConfig` em `INSTALLED_APPS` e incluir em cada papel:

```python
'catalog.view', 'pricing.view'
```

Somente `admin` e `manager` recebem:

```python
'catalog.manage', 'pricing.manage'
```

- [ ] **Step 4: Rodar teste e checks**

Run: `cd backend && python -m pytest tests/test_catalog_capabilities.py -q -o addopts='' && python manage.py check`

Expected: PASS e zero problemas.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog backend/config/settings/base.py backend/tenancy/capabilities.py backend/tests/test_catalog_capabilities.py
git commit -m "feat(catalog): scaffold catalog context"
```

### Task 2: Categorias, unidades e produtos

**Files:**
- Create: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0001_initial.py`
- Test: `backend/tests/test_catalog_models.py`

- [ ] **Step 1: Escrever testes de invariantes**

```python
import pytest
from django.core.exceptions import ValidationError

from catalog.models import Category, Product, Unit
from tenancy.models import Tenant


@pytest.mark.django_db
def test_product_sku_is_normalized_and_unique_per_tenant():
    tenant = Tenant.objects.create(name='Loja', slug='loja-catalog')
    unit = Unit.all_objects.create(tenant=tenant, symbol='kg', name='Quilograma', precision=3)
    first = Product.all_objects.create(tenant=tenant, sku=' racao-01 ', name='Ração', base_unit=unit)
    assert first.sku == 'RACAO-01'
    with pytest.raises(Exception):
        Product.all_objects.create(tenant=tenant, sku='racao-01', name='Outra', base_unit=unit)


@pytest.mark.django_db
def test_category_rejects_parent_cycle():
    tenant = Tenant.objects.create(name='Ciclo', slug='ciclo-catalog')
    parent = Category.all_objects.create(tenant=tenant, name='Pai')
    child = Category.all_objects.create(tenant=tenant, name='Filho', parent=parent)
    parent.parent = child
    with pytest.raises(ValidationError):
        parent.full_clean()
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_models.py -q -o addopts=''`

Expected: FAIL por ausência dos models.

- [ ] **Step 3: Implementar models tenant-scoped**

```python
class Unit(TimeStampedModel, TenantScopedModel):
    symbol = models.CharField(max_length=12)
    name = models.CharField(max_length=80)
    precision = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class Category(TimeStampedModel, TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, blank=True, default='')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

class Product(TimeStampedModel, TenantScopedModel):
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)
    base_unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    requires_lot = models.BooleanField(default=False)
    requires_expiry = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

Adicionar `UniqueConstraint` por tenant para símbolo e SKU, `CheckConstraint` para
`precision <= 6`, managers tenant-scoped e validação de ciclos e referências do mesmo tenant.

- [ ] **Step 4: Gerar e validar migration**

Run: `cd backend && python manage.py makemigrations catalog && python manage.py migrate --settings=config.settings.migration`

Expected: migration `catalog.0001_initial` aplicada.

- [ ] **Step 5: Rodar testes**

Run: `cd backend && python -m pytest tests/test_catalog_models.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/catalog backend/tests/test_catalog_models.py
git commit -m "feat(catalog): add category unit and product models"
```

### Task 3: Conversões e códigos de produto

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/services/conversions.py`
- Create: `backend/catalog/services/codes.py`
- Create: `backend/catalog/migrations/0002_productunit_productcode.py`
- Test: `backend/tests/test_catalog_conversions.py`
- Test: `backend/tests/test_product_codes.py`

- [ ] **Step 1: Escrever testes de conversão e GTIN**

```python
from decimal import Decimal

import pytest

from catalog.services.codes import validate_gtin
from catalog.services.conversions import to_base_quantity


def test_conversion_uses_decimal_and_unit_precision():
    assert to_base_quantity(Decimal('1.250'), Decimal('20')) == Decimal('25.000')


@pytest.mark.parametrize('code', ['7894900011517', '7891000315507'])
def test_valid_gtin_check_digit(code):
    assert validate_gtin(code) is True


def test_invalid_gtin_check_digit():
    assert validate_gtin('7894900011518') is False
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_conversions.py tests/test_product_codes.py -q -o addopts=''`

Expected: FAIL por módulos ausentes.

- [ ] **Step 3: Implementar conversão e models**

```python
def to_base_quantity(quantity: Decimal, factor: Decimal) -> Decimal:
    if quantity <= 0 or factor <= 0:
        raise ValueError('Quantity and factor must be positive.')
    return quantity * factor
```

`ProductUnit` contém produto, unidade, fator `Decimal(18, 6)`, vigência e estado.
`ProductCode` contém produto, tipo, valor normalizado, principal e estado. Criar constraints
para fator positivo, uma unidade ativa por produto e código ativo único por tenant.

- [ ] **Step 4: Implementar dígito verificador GTIN**

```python
def validate_gtin(value: str) -> bool:
    if not value.isdigit() or len(value) not in {8, 12, 13, 14}:
        return False
    digits = [int(item) for item in value]
    total = sum(digit * (3 if index % 2 == 0 else 1) for index, digit in enumerate(reversed(digits[:-1])))
    return (10 - total % 10) % 10 == digits[-1]
```

- [ ] **Step 5: Migrar e testar**

Run: `cd backend && python manage.py makemigrations catalog && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_catalog_conversions.py tests/test_product_codes.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/catalog backend/tests/test_catalog_conversions.py backend/tests/test_product_codes.py
git commit -m "feat(catalog): add commercial units and product codes"
```

### Task 4: Preços versionados e resolução por filial

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/services/pricing.py`
- Create: `backend/catalog/migrations/0003_productprice.py`
- Test: `backend/tests/test_catalog_pricing.py`

- [ ] **Step 1: Escrever testes de precedência e vigência**

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from catalog.services.pricing import resolve_effective_price


@pytest.mark.django_db
def test_branch_price_overrides_tenant_default(product, branch, tenant_price, branch_price):
    result = resolve_effective_price(product=product, branch=branch, at=timezone.now())
    assert result.amount == Decimal('12.90')


@pytest.mark.django_db
def test_default_price_is_used_without_branch_override(product, other_branch, tenant_price):
    result = resolve_effective_price(product=product, branch=other_branch, at=timezone.now())
    assert result.amount == Decimal('13.90')
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_pricing.py -q -o addopts=''`

Expected: FAIL por serviço/model ausente.

- [ ] **Step 3: Implementar `ProductPrice` e `BranchPrice`**

`ProductPrice` contém tenant, produto, valor `Decimal(18, 4)`, `valid_from`, `valid_to`,
estado e timestamps. `BranchPrice` contém os mesmos campos e filial obrigatória do mesmo
tenant. Adicionar constraints para valor não negativo e `valid_to > valid_from`. Usar
`ExclusionConstraint` PostgreSQL para impedir sobreposição por produto no preço padrão e
por produto/filial na sobrescrita.

- [ ] **Step 4: Implementar resolução determinística**

```python
def resolve_effective_price(*, product, branch, at):
    period = Q(valid_from__lte=at) & (Q(valid_to__isnull=True) | Q(valid_to__gt=at))
    branch_price = BranchPrice.objects.filter(
        product=product, branch=branch,
    ).filter(period).first()
    tenant_price = ProductPrice.objects.filter(product=product).filter(period).first()
    price = branch_price or tenant_price
    if price is None:
        raise PriceNotAvailable(product.id, branch.id)
    return price
```

- [ ] **Step 5: Migrar e testar**

Run: `cd backend && python manage.py makemigrations catalog && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_catalog_pricing.py -q -o addopts=''`

Expected: PASS, incluindo rejeição de períodos sobrepostos.

- [ ] **Step 6: Commit**

```bash
git add backend/catalog backend/tests/test_catalog_pricing.py
git commit -m "feat(catalog): add effective branch pricing"
```

### Task 5: RLS e isolamento do catálogo

**Files:**
- Create: `backend/catalog/migrations/0004_catalog_rls.py`
- Test: `backend/tests/test_catalog_rls.py`
- Test: `backend/tests/test_catalog_isolation.py`

- [ ] **Step 1: Escrever testes cross-tenant**

```python
@pytest.mark.django_db(transaction=True)
def test_product_from_other_tenant_is_hidden_by_rls(product_tenant_a, tenant_b_context):
    assert Product.all_objects.filter(pk=product_tenant_a.pk).exists() is False


@pytest.mark.django_db(transaction=True)
def test_cross_tenant_product_write_is_blocked(product_tenant_a, tenant_b_context):
    product_tenant_a.name = 'Ataque'
    with pytest.raises(DatabaseError):
        product_tenant_a.save(update_fields=['name'])
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_rls.py tests/test_catalog_isolation.py -q -o addopts=''`

Expected: FAIL porque as tabelas ainda não possuem policies.

- [ ] **Step 3: Criar migration RLS**

Aplicar `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY` e policies `USING` e
`WITH CHECK` baseadas em `current_setting('app.current_tenant_id', true)` para todas as
tabelas tenant-scoped do catálogo.

- [ ] **Step 4: Rodar isolamento**

Run: `cd backend && python manage.py migrate --settings=config.settings.migration && python -m pytest tests/test_catalog_rls.py tests/test_catalog_isolation.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog/migrations/0004_catalog_rls.py backend/tests/test_catalog_rls.py backend/tests/test_catalog_isolation.py
git commit -m "feat(catalog): enforce catalog row-level security"
```

### Task 6: APIs do catálogo

**Files:**
- Create: `backend/catalog/serializers.py`
- Create: `backend/catalog/permissions.py`
- Create: `backend/catalog/views.py`
- Create: `backend/catalog/urls.py`
- Modify: `backend/config/urls.py`
- Test: `backend/tests/test_catalog_api.py`
- Test: `backend/tests/test_catalog_idor.py`

- [ ] **Step 1: Escrever testes de CRUD, capability e IDOR**

```python
@pytest.mark.django_db
def test_manager_creates_product(api_client, manager, tenant, unit):
    authenticate_with_mfa(api_client, manager, tenant)
    response = api_client.post('/api/v1/products/', {
        'sku': 'RACAO-20KG', 'name': 'Ração 20 kg', 'base_unit': str(unit.id),
    }, format='json', HTTP_X_TENANT_ID=str(tenant.id))
    assert response.status_code == 201


@pytest.mark.django_db
def test_operator_cannot_manage_catalog(api_client, operator, tenant, unit):
    authenticate_with_mfa(api_client, operator, tenant)
    response = api_client.post('/api/v1/products/', {
        'sku': 'BLOCKED', 'name': 'Bloqueado', 'base_unit': str(unit.id),
    }, format='json', HTTP_X_TENANT_ID=str(tenant.id))
    assert response.status_code == 403
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_api.py tests/test_catalog_idor.py -q -o addopts=''`

Expected: FAIL com 404 nas rotas.

- [ ] **Step 3: Implementar serializers e viewsets**

Usar `ModelViewSet` com querysets tenant-scoped, paginação DRF, `select_related`, busca
normalizada, filtros permitidos e `perform_destroy` substituído por inativação. Validar
filial, categoria e unidade no tenant ativo antes de salvar.

- [ ] **Step 4: Implementar preço vigente**

Criar action GET que valida `branch_id`, autorização de filial e `at` ISO-8601, chama
`resolve_effective_price` e retorna ID, valor, moeda, origem `tenant|branch` e vigência.

- [ ] **Step 5: Rodar testes das APIs**

Run: `cd backend && python -m pytest tests/test_catalog_api.py tests/test_catalog_idor.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/catalog backend/config/urls.py backend/tests/test_catalog_api.py backend/tests/test_catalog_idor.py
git commit -m "feat(catalog): expose secure catalog APIs"
```

### Task 7: Auditoria, Outbox e contratos

**Files:**
- Create: `backend/catalog/services/events.py`
- Modify: `backend/catalog/views.py`
- Modify: `docs/03_Domain/DOMAIN_EVENT_CATALOG.md`
- Modify: `docs/05_API/openapi.yaml`
- Test: `backend/tests/test_catalog_observability.py`

- [ ] **Step 1: Escrever teste transacional**

```python
@pytest.mark.django_db(transaction=True)
def test_product_creation_persists_audit_and_outbox(api_client, manager, tenant, unit):
    authenticate_with_mfa(api_client, manager, tenant)
    response = create_product(api_client, tenant, unit)
    product_id = response.json()['id']
    assert AuditRecord.objects.filter(action='catalog.product.created', resource_id=product_id).exists()
    assert OutboxEvent.objects.filter(event_type='catalog.product.created', aggregate_id=product_id).exists()
```

- [ ] **Step 2: Confirmar falha inicial**

Run: `cd backend && python -m pytest tests/test_catalog_observability.py -q -o addopts=''`

Expected: FAIL por ausência dos registros.

- [ ] **Step 3: Persistir auditoria e Outbox atomicamente**

Criar serviço que recebe ator, tenant, aggregate e payload mínimo, chama os serviços
existentes dentro da mesma `transaction.atomic()` da alteração e nunca inclui preço de
custo, credenciais ou dados sensíveis.

- [ ] **Step 4: Documentar OpenAPI e eventos**

Adicionar schemas, exemplos, filtros, paginação e erros estáveis para todas as rotas, além
das versões `catalog.product.created.v1`, `catalog.product.updated.v1`,
`catalog.price.changed.v1` e `catalog.product.deactivated.v1`.

- [ ] **Step 5: Testar e validar OpenAPI**

Run: `cd backend && python -m pytest tests/test_catalog_observability.py -q -o addopts=''`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/catalog docs/03_Domain/DOMAIN_EVENT_CATALOG.md docs/05_API/openapi.yaml backend/tests/test_catalog_observability.py
git commit -m "feat(catalog): audit catalog changes and events"
```

### Task 8: Gate e encerramento da Sprint 2

**Files:**
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `docs/PRD.md`
- Create: `docs/10_Releases/SPRINT-002_Catalog_Final_Report.md`
- Modify: `docs/10_Releases/MILESTONE-001_MANIFEST.txt`

- [ ] **Step 1: Rodar gate local completo**

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

Expected: zero migrations pendentes, zero falhas e cobertura mínima de 80% mantida.

- [ ] **Step 2: Validar segredos e dependências**

Run:

```bash
python -m pip freeze --exclude-editable > requirements-audit.txt
pip-audit --strict --requirement requirements-audit.txt
cd ..
git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline
```

Expected: nenhum achado novo ou vulnerabilidade conhecida.

- [ ] **Step 3: Atualizar documentação e checklist**

Documentar setup, endpoints, evidências, riscos residuais e marcar somente itens
comprovados da Sprint 2 em `docs/PRD.md`.

- [ ] **Step 4: Regenerar manifesto**

Gerar linhas ordenadas `caminho<TAB>bytes<TAB>sha256` para todos os arquivos de `docs`,
excluindo o próprio manifesto e ZIPs.

- [ ] **Step 5: Commit final**

```bash
git add README.md backend/README.md docs
git commit -m "feat: sprint 2 - catalogo e cadastros-base"
```

- [ ] **Step 6: Integrar e validar CI**

Enviar para `master`, acompanhar GitHub Actions até ficar verde e manter abertos no PRD os
itens de integração enquanto a execução remota não estiver concluída.
