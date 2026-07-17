# Sprint 3 — Estoque e Movimentações — Relatório Parcial de Hardening

Data da revisão: 2026-07-17

## Resultado desta rodada

A Sprint 3 estava em estado parcial, com APIs não importáveis, serializers apontando para campos inexistentes e rotas não registradas. O hardening desta rodada estabilizou o núcleo técnico do módulo `inventory` para permitir evolução segura nas próximas tarefas.

Correções aplicadas:

- models de estoque alinhados ao contrato usado pelos serializers e services;
- `version` adicionado às entidades de estoque;
- `branch` e `actor` adicionados a `StockOperation`;
- serializers corrigidos para campos existentes e validação por `full_clean()`;
- `inventory.permissions` criado;
- `inventory.urls` criado e incluído em `config.urls`;
- views reescritas sem relações inexistentes e com querysets tenant-scoped;
- `StockMovement` e `StockBalance` expostos como somente leitura;
- services simplificados para recibo, saída, ajuste, transferência, reversão, reserva e saldo;
- testes de hardening adicionados para importação, serializers e rotas.

## Evidências

Comandos executados com sucesso:

```text
C:\ERP\.venv\Scripts\python.exe manage.py check
Resultado: System check identified no issues (0 silenced).
```

```text
C:\ERP\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
Resultado: No changes detected.
```

```text
C:\ERP\.venv\Scripts\python.exe manage.py migrate --settings=config.settings.migration
Resultado: inventory.0002, inventory.0003 e inventory.0004 aplicadas com sucesso.
```

```text
C:\ERP\.venv\Scripts\python.exe -m ruff check inventory tests/test_inventory_api_hardening.py tests/test_inventory_capabilities.py tests/test_stock_locations.py tests/test_stock_lots.py
Resultado: All checks passed!
```

```text
C:\ERP\.venv\Scripts\python.exe -m pytest tests/test_inventory_api_hardening.py tests/test_inventory_capabilities.py -q -o addopts=''
Resultado: 29 passed, 1 warning.
```

```text
C:\ERP\.venv\Scripts\python.exe -m pytest tests/test_stock_locations.py tests/test_stock_lots.py --collect-only -q -o addopts=''
Resultado: 7 tests collected.
```

## Limitação de ambiente

A execução dos testes que usam banco continua travando por timeout no ambiente local, mesmo com coleta funcionando. Isso já havia ocorrido no hardening da Sprint 2.

Comando afetado:

```text
C:\ERP\.venv\Scripts\python.exe -m pytest tests/test_stock_locations.py tests/test_stock_lots.py -q -o addopts=''
Resultado: timeout após 184s.
```

Também foi confirmado que `manage.py migrate` com o usuário runtime falha por ausência de permissão DDL no schema `public`; a aplicação correta é via `config.settings.migration`, coerente com a estratégia de owner separado.

## Pendências funcionais da Sprint 3

Ainda não considerar a Sprint 3 encerrada. Permanecem pendentes:

- exigir lote/validade conforme flags do produto;
- bloquear movimentação comum de lote vencido;
- implementar chave de idempotência obrigatória nas APIs de escrita;
- rejeitar replay de idempotência com payload diferente;
- provar concorrência sem overselling;
- aplicar e validar RLS nas tabelas novas;
- implementar reconciliação de saldo versus movimentos;
- documentar OpenAPI de estoque e eventos finais;
- executar suíte com banco em ambiente saudável.

## Status

Status técnico: núcleo de inventory carregável, lint limpo, serializers e rotas estabilizados.

Status da Sprint 3: em execução, não concluída.
