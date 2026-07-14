# Documentation Changelog

Todas as mudanças relevantes na base documental são registradas aqui.

## 2026-07-14 — Documentation Foundation v0.1.0

### Added

- Foundation Design consolidando decisões extraídas da conversa.
- Plano de implementação da baseline documental.
- Estrutura documental centralizada em `C:\ERP\docs`.
- Padrão de documentos, índice e porta de entrada.
- Primeiros drafts de governança e produto.
- Seis ADRs fundamentais, SAD, Engineering Handbook e desenho de domínio.
- PRD Master, SRS e matriz inicial de rastreabilidade.
- Padrões REST/OpenAPI, catálogo de erros, segurança multi-tenant e threat model.

### Decisions

- Monólito modular Django.
- PostgreSQL compartilhado com `tenant_id` e RLS.
- Hierarquia `Tenant → Empresa → Filial`.
- PDV Electron online por padrão, com contingência offline restrita.
- Provedor fiscal contratado e pago pelo cliente no MVP.
- IA fora do MVP, com preparação arquitetural para adoção futura.

### Archived

- Pacote inicial de cinco rascunhos em `99_Archive/initial-package`.
- PRD original e fonte HTML em `99_Archive/source-prd`.
