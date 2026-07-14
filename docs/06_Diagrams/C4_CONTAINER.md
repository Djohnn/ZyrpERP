# C4 — Contêineres

**ID:** DIA-002  
**Versão:** 0.1.0  
**Status:** Review

```mermaid
flowchart TB
    web["Aplicação Web\nReact"]
    pdv["PDV Desktop\nElectron + React + SQLite"]
    api["API / Backend\nDjango + DRF\nMonólito modular"]
    worker["Workers assíncronos\nCelery"]
    db[("PostgreSQL\nTenant ID + RLS")]
    redis[("Redis\nFila e cache")]
    storage[("Armazenamento de objetos")]
    fiscal["Provedor fiscal"]
    obs["Logs, métricas e traces"]

    web -->|"HTTPS / JSON"| api
    pdv -->|"HTTPS / sync idempotente"| api
    pdv -->|"contingência local restrita"| local[("SQLite local")]
    api --> db
    api --> redis
    api --> storage
    worker --> redis
    worker --> db
    worker --> fiscal
    api --> obs
    worker --> obs
```

## Regras arquiteturais

- Web e PDV nunca acessam PostgreSQL diretamente.
- Processos demorados e integrações externas são assíncronos quando compatível com a experiência do usuário.
- A Transactional Outbox conecta transações de domínio ao processamento assíncrono.
- SQLite existe apenas no PDV e não substitui o registro central de forma permanente.

