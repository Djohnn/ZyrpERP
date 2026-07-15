# Sprint 2 — Catálogo e Cadastros-base

## 1. Objetivo

Entregar um catálogo multi-tenant seguro para itens vendáveis, com categorias, unidades,
conversões comerciais, múltiplos códigos e preços padrão ou específicos por filial. A
entrega deve sustentar casas de rações sem acoplar estoque, compras ou vendas ao catálogo.

## 2. Escopo

Inclui:

- categorias hierárquicas opcionais;
- unidades de medida e precisão decimal;
- produto vendável representado por SKU independente;
- unidade base e conversões comerciais por produto;
- códigos internos, EAN, GTIN e códigos alternativos;
- preços versionados por vigência;
- preço padrão do tenant e sobrescrita opcional por filial;
- ativação e inativação sem exclusão física;
- APIs, auditoria, Outbox, permissões, RLS e testes.

Não inclui clientes, fornecedores, promoções, estoque, compras, vendas, regras tributárias
detalhadas, kits, composição, variantes complexas ou múltiplas tabelas comerciais.

## 3. Arquitetura

O app Django `catalog` será um bounded context independente dentro do monólito modular.
Ele dependerá de `tenancy` para tenant, empresa, filial e autorização; de `audit` para
trilha administrativa; e de `outbox` para eventos transacionais. `inventory`, `sales` e
outros módulos futuros dependerão dos contratos públicos de `catalog`, nunca de detalhes
internos de persistência.

Entidades tenant-scoped usarão `tenant_id` obrigatório, manager seguro, contexto explícito
e RLS no PostgreSQL. Filiais referenciadas por preço devem pertencer ao mesmo tenant.

## 4. Modelo de domínio

### 4.1 Category

- UUID, tenant, nome, código opcional, categoria pai opcional e estado ativo;
- hierarquia sem ciclos;
- nome e código normalizados e únicos no escopo necessário do tenant;
- inativação preserva produtos e histórico.

### 4.2 Unit

- UUID, tenant, símbolo, nome, precisão decimal e estado ativo;
- símbolos como `UN`, `KG`, `G`, `SC` e `CX` são configuráveis pelo tenant;
- precisão define quantização aceita, sem uso de `float`.

### 4.3 Product

- UUID, tenant, SKU, nome, descrição, categoria opcional e unidade base;
- flags `is_active`, `requires_lot` e `requires_expiry`;
- cada combinação efetivamente vendável é um SKU independente;
- SKU normalizado e único por tenant;
- não há exclusão física pela API.

### 4.4 ProductUnit

- produto, unidade comercial e fator positivo para a unidade base;
- exemplo: `1 SC = 20 KG`;
- unidade base equivale ao fator `1` e não é duplicada como conversão;
- conversão utilizada por fatos posteriores não pode ser alterada; uma nova versão deve
  ser criada e os consumidores preservam o fator aplicado.

### 4.5 ProductCode

- produto, tipo `internal`, `ean`, `gtin` ou `supplier`, valor normalizado e estado;
- código não pode apontar para dois produtos ativos do mesmo tenant;
- validação estrutural de EAN/GTIN inclui tamanho e dígito verificador;
- um produto pode ter vários códigos e um código pode ser marcado como principal.

### 4.6 ProductPrice

- produto, valor `Decimal`, início de vigência, fim opcional e estado;
- preço deve ser maior ou igual a zero;
- períodos do mesmo escopo não podem se sobrepor;
- preço padrão é tenant-scoped; `BranchPrice` adiciona filial do mesmo tenant;
- resolução recebe produto, filial e instante: busca preço vigente da filial e usa o
  padrão como fallback;
- preço histórico não é sobrescrito.

## 5. Autorização

Capabilities iniciais:

- `catalog.view`: admin, manager e operator;
- `catalog.manage`: admin e manager;
- `pricing.view`: admin, manager e operator;
- `pricing.manage`: admin e manager.

Escopo de filial é validado tanto na escrita quanto na resolução de preço. Recurso de
outro tenant ou filial não autorizada retorna 404 quando a existência não deve ser
revelada. Operações administrativas exigem sessão com MFA conforme a política vigente.

## 6. API

Rotas em `/api/v1/`:

- `/categories/` e `/categories/{id}/`;
- `/units/` e `/units/{id}/`;
- `/products/` e `/products/{id}/`;
- `/products/{id}/units/`;
- `/products/{id}/codes/`;
- `/products/{id}/prices/`;
- `/products/{id}/branch-prices/`;
- `/products/{id}/effective-price/?branch_id=&at=`.

Listagens têm paginação, busca, filtros por estado/categoria/código e ordenação limitada a
campos seguros. Escritas usam validação otimista e retornam erros RFC 9457 com códigos
estáveis: `duplicate_sku`, `duplicate_product_code`, `invalid_conversion_factor`,
`overlapping_price_period` e `price_not_available`.

## 7. Transações, auditoria e eventos

Alterações compostas usam `transaction.atomic()`. Auditoria registra ator, tenant,
recurso, ação e campos não sensíveis. Eventos Outbox são persistidos na mesma transação,
com versões explícitas, incluindo `catalog.product.created`, `catalog.product.updated`,
`catalog.price.changed` e `catalog.product.deactivated`.

## 8. Qualidade e segurança

- testes unitários de normalização, conversão, EAN/GTIN, vigência e resolução de preço;
- testes de API para capabilities, MFA, filtros, erros e inativação;
- testes cross-tenant, RLS, IDOR e filial não autorizada;
- testes de concorrência para SKU, código e períodos de preço;
- rollback conjunto de domínio, auditoria e Outbox;
- OpenAPI, migrations, Ruff, mypy, cobertura, deploy check, auditoria de dependências e
  detecção de segredos obrigatórios;
- regressão integral das Sprints 0 e 1.

## 9. Critérios de aceite

- catálogo nunca vaza dados entre tenants;
- produto possui SKU único, unidade base e códigos consistentes;
- conversões decimais são determinísticas e não perdem precisão;
- preço vigente resolve corretamente filial, fallback e instante;
- produtos inativos não entram em novas operações;
- mudanças relevantes são auditadas e publicadas pela Outbox;
- suíte completa e CI remota terminam sem falhas.

## 10. Preparação para evolução

O modelo permite adicionar agrupamento de produtos, tabelas comerciais, promoções,
tributação e cadastros de parceiros sem alterar a identidade do SKU. Nenhuma dessas
extensões será implementada na Sprint 2.
