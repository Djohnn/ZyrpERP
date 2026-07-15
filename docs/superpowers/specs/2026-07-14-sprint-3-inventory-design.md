# Sprint 3 — Estoque e Movimentações

## 1. Objetivo

Entregar estoque multi-tenant por filial e local, calculado por movimentos imutáveis,
com lotes opcionais, transferências atômicas, idempotência e bloqueio absoluto de saldo
negativo. A Sprint 3 depende do catálogo validado na Sprint 2.

## 2. Escopo

Inclui:

- múltiplos locais por filial e local principal automático;
- lotes e validade opcionais conforme configuração do produto;
- saldo inicial, entrada, saída, ajuste, transferência e reversão;
- saldo projetado por produto, filial, local e lote;
- movimentos imutáveis e operação agregadora;
- idempotência, concorrência, auditoria, Outbox, RLS e APIs de consulta.

Não inclui compras, reservas de venda, custo médio, custo contábil, inventário por coletor,
serialização individual, FEFO automático, produção, composição ou estoque offline do PDV.

## 3. Arquitetura

O app Django `inventory` consome a identidade e as conversões públicas de `catalog`. O
modelo separa fatos (`StockMovement`) de projeção (`StockBalance`). Nenhum consumidor
altera saldo diretamente: toda mudança ocorre por um serviço transacional que cria a
operação, bloqueia saldos, valida invariantes, grava movimentos, atualiza projeções,
audita e persiste eventos Outbox.

Todas as tabelas operacionais têm tenant obrigatório e RLS. Acesso também é limitado às
filiais autorizadas do usuário. O banco usa constraints para reforçar quantidades,
direções e unicidade das chaves de idempotência.

## 4. Modelo de domínio

### 4.1 StockLocation

- UUID, tenant, filial, código, nome, tipo e estado ativo;
- cada filial possui exatamente um local principal ativo;
- código é único dentro da filial;
- local com histórico não é apagado.

### 4.2 StockLot

- UUID, tenant, produto, número do lote, fabricação opcional e validade opcional;
- lote é único por produto e tenant;
- `requires_lot` obriga lote em toda entrada ou saída;
- `requires_expiry` obriga validade;
- movimentar lote vencido é rejeitado por padrão, exceto ajuste de baixa explicitamente
  identificado e autorizado.

### 4.3 StockOperation

- UUID, tenant, tipo, estado, chave de idempotência, ator, motivo e correlação;
- agrupa um ou mais movimentos pertencentes à mesma transação de negócio;
- tipos: `opening`, `receipt`, `issue`, `adjustment`, `transfer` e `reversal`;
- operação confirmada não é editada ou apagada.

### 4.4 StockMovement

- UUID, tenant, operação, produto, filial, local, lote opcional, direção e quantidade base;
- quantidade é positiva e quantizada conforme a unidade base;
- direção determina entrada ou saída; não se grava quantidade negativa;
- preserva unidade comercial, fator e quantidade informados na origem;
- registro confirmado é imutável inclusive via ORM e administração.

### 4.5 StockBalance

- tenant, produto, filial, local, lote opcional e quantidade base atual;
- constraint única representa uma linha de saldo por dimensão;
- é projeção reconstruível a partir dos movimentos;
- toda atualização usa `SELECT ... FOR UPDATE` em ordem determinística;
- constraint e serviço impedem quantidade menor que zero.

### 4.6 Idempotência

A chave é única por tenant, operação e cliente chamador. Repetição com o mesmo payload
retorna o resultado original. Repetição com payload diferente retorna
`idempotency_conflict`. A resposta persistida não contém dados sensíveis.

## 5. Regras operacionais

- estoque negativo é sempre proibido no MVP;
- transferências geram saída e entrada na mesma transação;
- falha em qualquer lado reverte toda a operação;
- transferência entre filiais exige autorização nas duas filiais;
- ajuste exige motivo, capability administrativa e MFA;
- correção usa reversão compensatória vinculada à operação original;
- uma operação só pode ser revertida uma vez;
- produto ou local inativo não aceita nova movimentação;
- unidade comercial é convertida para a base pelo fator versionado do catálogo;
- quantidade zero, fator inválido e precisão excedida são rejeitados.

## 6. Autorização

Capabilities iniciais:

- `inventory.view`: admin, manager e operator nas filiais autorizadas;
- `inventory.receive`: admin, manager e operator autorizado;
- `inventory.issue`: admin, manager e operator autorizado;
- `inventory.transfer`: admin e manager;
- `inventory.adjust`: admin e manager com MFA;
- `inventory.locations.manage`: admin e manager com MFA.

Recursos cross-tenant ou fora do escopo de filial retornam 404 quando necessário para
evitar enumeração.

## 7. API

Rotas em `/api/v1/`:

- `/stock-locations/` e `/stock-locations/{id}/`;
- `/stock-lots/` e `/stock-lots/{id}/`;
- `/stock-balances/`;
- `/stock-movements/` e `/stock-movements/{id}/` somente leitura;
- `/stock-operations/opening/`;
- `/stock-operations/receipts/`;
- `/stock-operations/issues/`;
- `/stock-operations/adjustments/`;
- `/stock-operations/transfers/`;
- `/stock-operations/{id}/reverse/`.

Escritas exigem `Idempotency-Key`. Erros usam RFC 9457 e códigos estáveis:
`insufficient_stock`, `lot_required`, `expiry_required`, `expired_lot`,
`inactive_stock_dimension`, `invalid_stock_precision`, `idempotency_conflict`,
`operation_already_reversed`, `branch_access_denied` e `stock_movement_immutable`.

## 8. Concorrência e consistência

Serviços ordenam locks por tenant, produto, filial, local e lote para reduzir deadlocks.
Saídas concorrentes do mesmo saldo são serializadas. Se o saldo disponível não cobrir a
quantidade, nenhuma parte da operação é gravada. Deadlocks transitórios podem ser
repetidos somente no limite do serviço e sempre com a mesma chave idempotente.

Uma rotina de reconciliação compara a soma dos movimentos com `StockBalance`, gera
métrica e alerta sobre divergência e nunca corrige silenciosamente o saldo.

## 9. Auditoria e eventos

Auditoria registra criação, confirmação, rejeição, ajuste, transferência e reversão sem
payload sensível. Eventos Outbox na mesma transação incluem `inventory.stock.changed`,
`inventory.transfer.completed`, `inventory.adjustment.completed` e
`inventory.operation.reversed`. Consumidores recebem ID da operação e dimensões mínimas,
com versão explícita e sem depender do formato interno dos models.

## 10. Qualidade e segurança

- testes unitários de conversão, precisão, lote, validade e reversão;
- testes transacionais de entrada, saída, ajuste e transferência;
- testes concorrentes provando ausência de overselling e saldo negativo;
- testes de rollback entre os dois lados da transferência;
- repetição idempotente e conflito de payload;
- imutabilidade no service, ORM, admin e API;
- testes cross-tenant, RLS, IDOR e acesso às duas filiais;
- reconciliação de movimentos e projeção;
- auditoria e Outbox transacionais;
- migrations, Ruff, mypy, cobertura, deploy check, dependências, segredos e regressão
  completa das Sprints anteriores.

## 11. Critérios de aceite

- nenhuma operação produz saldo negativo;
- concorrência não permite consumir a mesma disponibilidade duas vezes;
- transferências são integralmente confirmadas ou revertidas;
- movimentos confirmados são imutáveis e correções são compensatórias;
- lotes e validades obedecem a configuração do produto;
- idempotência impede duplicidade e detecta payload conflitante;
- isolamento de tenant e filial passa por aplicação e RLS;
- projeção é reconciliável com os movimentos;
- CI remota termina sem falhas.
