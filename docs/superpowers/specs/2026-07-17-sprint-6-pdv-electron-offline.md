# Sprint 6 — PDV Electron Offline

## 1. Objetivo

Tornar o PDV Electron funcional em modo offline, com fila local de operações, sincronização bidirecional automática ao reconectar, e resolução de conflitos. A Sprint 6 depende do PDV online (Sprint 5) e das APIs de venda/caixa (Sprint 4).

## 2. Escopo

### Inclui:

- Detecção de conectividade (online/offline)
- Journal SQLite append-only para operações pendentes
- Cache completo de catálogo (produtos, preços, unidades) sincronizado periodicamente
- Fila de vendas offline com replay ao reconectar
- Operações de caixa (abrir/fechar) offline
- Sincronização bidirecional automática com resolução de conflitos
- Indicador visual de status de conexão
- Limpeza de journal após sync bem-sucedido

### Não inclui:

- Integração fiscal (Sprint 7)
- Integração com maquineta de cartão
- Gestão de dispositivos via painel web
- UI/UX avançada
- Multi-tenant offline complexo

## 3. Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                    PDV Electron App                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Renderer (React)                                    │   │
│  │  - Indicador online/offline                          │   │
│  │  - Notificação de fila pendente                      │   │
│  │  - Botão "Sincronizar" manual                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↕ IPC                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Main Process                                        │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────┐  │   │
│  │  │ Sync     │  │ Offline   │  │ Connectivity     │  │   │
│  │  │ Engine   │─▶│ Queue     │  │ Monitor          │  │   │
│  │  └──────────┘  │ (Journal) │  └──────────────────┘  │   │
│  │                 └───────────┘                        │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Conflict Resolver                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 4. Modelo de Dados (SQLite)

### 4.1 operation_journal

```sql
CREATE TABLE operation_journal (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL UNIQUE,          -- UUID v4 gerado localmente
  type TEXT NOT NULL,                  -- 'sale:create' | 'cash-session:open' | 'cash-session:close'
  payload TEXT NOT NULL,               -- JSON do corpo da requisição
  idempotency_key TEXT NOT NULL UNIQUE,-- Para replay seguro
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending' | 'syncing' | 'synced' | 'conflict' | 'failed'
  created_at TEXT NOT NULL,            -- ISO 8601
  synced_at TEXT,                      -- ISO 8601, null até sincronizar
  retry_count INTEGER DEFAULT 0,
  last_error TEXT,
  conflict_resolution TEXT              -- JSON com resolução se houver conflito
);

CREATE INDEX idx_journal_status ON operation_journal(status);
CREATE INDEX idx_journal_created ON operation_journal(created_at);
```

### 4.2 catalog_cache (expandido da Sprint 5)

```sql
-- Adicionar à tabela products existente:
ALTER TABLE products ADD COLUMN last_synced_at TEXT;

-- Nova tabela para metadados de sync:
CREATE TABLE sync_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

INSERT INTO sync_metadata (key, value, updated_at) VALUES
  ('last_catalog_sync', '0', '1970-01-01T00:00:00Z'),
  ('last_operations_sync', '0', '1970-01-01T00:00:00Z'),
  ('schema_version', '2', '2026-07-17T00:00:00Z');
```

### 4.3 connectivity_state (em memória + localStorage)

```typescript
interface ConnectivityState {
  isOnline: boolean;
  lastOnlineAt: Date | null;
  lastOfflineAt: Date | null;
  pendingOperations: number;
  lastSyncAt: Date | null;
}
```

## 5. Fluxos

### 5.1 Detecção de Conectividade

```
1. App inicia → verifica conectividade
   - Ping no backend: GET /api/v1/health/
   - Resposta 200 → online
   - Timeout/falha → offline
2. Monitor contínuo:
   - Evento window 'online'/'offline' (Electron net module)
   - Ping periódico a cada 30s
   - Transição: notifica renderer via IPC
3. Armazena estado em localStorage + memória
```

### 5.2 Operação Online vs Offline

```
AO CRIAR VENDA:
  if online:
    1. POST /api/v1/sales/counter/ (como Sprint 5)
    2. Se sucesso → pronto
    3. Se falha de rede → cai para offline
  if offline:
    1. Gera UUID + idempotency_key
    2. Salva no operation_journal { type: 'sale:create', payload, status: 'pending' }
    3. Atualiza UI: "Venda registrada localmente (1 pendente)"
    4. Inicia sync quando online

AO ABRIR/FECHAR CAIXA:
  if offline:
    1. Registra no journal (mesmo fluxo)
    2. Caixa marcado como 'local' — válido apenas localmente
    3. Ao sync: cria no backend + reconcilia
```

### 5.3 Sincronização

```
SYNC ENGINE (executa em loop quando online):
  1. Busca operations pendentes do journal (status = 'pending')
  2. Para cada operation (ordenada por created_at ASC):
     a. Marca como 'syncing'
     b. Replay: chama API correspondente com idempotency_key
     c. Se 201/200 → marca como 'synced', salva synced_at
     d. Se 409/422 (conflito) → marca como 'conflict'
        - Aplica regra: "last-write-wins" para vendas
        - Para caixa: "server-wins" (caixa remoto tem prioridade)
     e. Se erro de rede → marca como 'pending', retry após backoff
     f. Se 4xx não recuperável → marca como 'failed', notifica usuário
  3. Após sync de operations, sync catálogo
  4. Apaga registros 'synced' com mais de 7 dias (cleanup)

BACKOFF EXPONENCIAL:
  - 1ª tentativa: 5s
  - 2ª: 15s
  - 3ª: 45s
  - 4+: 120s (max)
  - Reset após sync bem-sucedido
```

### 5.4 Resolução de Conflitos

```typescript
// Estratégias por tipo de operação
const CONFLICT_STRATEGIES = {
  'sale:create': 'last-write-wins',     // Venda é criada com novos IDs
  'cash-session:open': 'server-wins',   // Sessão remota prevalece
  'cash-session:close': 'last-write-wins', // Fechamento mais recente vale
};

// Regras:
// 1. sale:create → sempre cria nova venda (idempotency garante unicidade)
// 2. cash-session:open → se já existe sessão aberta no server, usa ela
// 3. cash-session:close → se divergência de valores, vence o último
```

### 5.5 Cache de Catálogo (Sync Periódico)

```
1. A cada 5 minutos (quando online):
   GET /api/v1/products/?page_size=100&updated_after=<last_sync>
2. Para cada página:
   a. Atualiza/Upsert na tabela products
   b. Para cada produto: GET /api/v1/products/<id>/prices/
   c. Atualiza/Upsert na tabela prices
3. Atualiza sync_metadata['last_catalog_sync']
4. Se delta for grande (>1000 produtos), usa background throttling
```

## 6. APIs Utilizadas

### 6.1 Existentes (Sprint 4 + 5)

| Método | Endpoint | Uso |
|--------|----------|-----|
| POST | `/api/v1/devices/validate/` | Auth |
| POST | `/api/v1/devices/refresh/` | Refresh token |
| POST | `/api/v1/cash-sessions/open/` | Abrir caixa |
| GET | `/api/v1/cash-sessions/current/` | Status caixa |
| POST | `/api/v1/cash-sessions/<id>/close/` | Fechar caixa |
| POST | `/api/v1/sales/counter/` | Criar venda |
| GET | `/api/v1/products/` | Buscar/listar produtos |
| GET | `/api/v1/products/<id>/prices/` | Preços do produto |

### 6.2 Novas (Sprint 6)

| Método | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | `/api/v1/health/` | — | `{ status: "ok" }` |
| POST | `/api/v1/sync/batch/` | `{ operations: [{ type, payload, idempotency_key }] }` | `{ results: [{ status, data, error }] }` |

O endpoint `/api/v1/sync/batch/` permite enviar múltiplas operações de uma vez, reduzindo round-trips.

## 7. Componentes Frontend (Novos)

### SyncIndicator
- Ícone na barra superior: verde (online), amarelo (sincronizando), vermelho (offline)
- Tooltip: "Online" / "Offline - X pendentes" / "Sincronizando..."
- Botão "Sincronizar agora" quando há pendentes

### SyncStatusBar
- Barra inferior opcional
- Mostra: "Último sync: 5 min atrás"
- Barra de progresso durante sync

## 8. Testes

### 8.1 Unitários (Vitest + SQLite in-memory)

- `operation_journal.test.ts`:
  - Salva operação no journal
  - Marca como synced após sucesso
  - Retry incrementa contador
  - Cleanup remove registros antigos

- `sync_engine.test.ts`:
  - Processa fila vazia (no-op)
  - Processa 1 operação com sucesso
  - Processa operação com falha de rede (retry)
  - Processa operação com conflito 409
  - Backoff exponencial

- `connectivity_monitor.test.ts`:
  - Detecta online no startup
  - Detecta offline após timeout
  - Transição online→offline→online

### 8.2 Integração (Vitest + MSW)

- `offline_sale.test.ts`:
  - Venda falha → cai para offline → registra no journal
  - Venda offline → volta online → sync automático
  - Múltiplas vendas offline → batch sync

### 8.3 E2E (Playwright)

- `offline.spec.ts`:
  - Desconectar rede → fazer venda → reconectar → ver sync
  - Ver indicador de conectividade
  - Ver catálogo em cache offline

## 9. Estrutura do Projeto (Adições)

```
pdv/src/main/
├── services/
│   ├── syncEngine.ts         # NOVO: coordena sync
│   ├── operationJournal.ts   # NOVO: gerencia SQLite journal
│   ├── connectivityMonitor.ts# NOVO: detecta online/offline
│   └── conflictResolver.ts   # NOVO: resolve conflitos
├── ipc/
│   ├── sync.ts               # NOVO: handlers IPC de sync
│   └── connectivity.ts       # NOVO: handlers IPC de conectividade
└── utils/
    └── backoff.ts            # NOVO: backoff exponencial
```

## 10. Critérios de Aceite

- [ ] App detecta perda de conexão em <5s
- [ ] App detecta restauração de conexão em <5s
- [ ] Venda offline é salva no journal
- [ ] Ao reconectar, venda offline é sincronizada automaticamente
- [ ] Caixa pode ser aberto/fechado offline
- [ ] Catálogo em cache permite busca offline
- [ ] Idempotency key previne duplicação no sync
- [ ] Conflitos são resolvidos por estratégia por tipo
- [ ] Indicador visual mostra status de conexão
- [ ] Botão "Sincronizar agora" força sync manual
- [ ] Retry com backoff exponencial
- [ ] Journal faz cleanup de registros antigos (>7 dias)
- [ ] Testes unitários passam (journal, sync, connectivity)
- [ ] Testes E2E passam (fluxo offline→online)
- [ ] Build continua gerando instaladores
- [ ] Ruff e mypy do backend continuam passando

## 11. Fora do Escopo (Sprint 7+)

- Integração fiscal (NF-e/NFC-e)
- Integração com maquineta de cartão
- Dashboard web de monitoramento de PDVs
- Multi-idioma
- Nota promissória / venda fiado
- Devolução de venda (Sprint 7)

## 12. Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| SQLite corrompido em queda de energia | Perda de journal | WAL mode + backup periódico |
| Conflito não resolvível | Venda ou caixa inconsistente | Log + notificação para admin |
| Sync lento com muitas operações | UX degradada | Batch endpoint + progresso visual |
| Token expira durante offline | Sync falha após reconectar | Refresh token ao voltar, se falhar → relogin |
| Cache de catálogo muito grande | App lento | Paginação no sync, LRU eviction |

## 13. Histórico

| Versão | Data | Alteração |
|--------|------|-----------|
| 0.1.0 | 2026-07-17 | Design inicial da Sprint 6 |
