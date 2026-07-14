# DOC-STD-001 — Documentation Standard

| Campo | Valor |
|---|---|
| Código | DOC-STD-001 |
| Título | Documentation Standard |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Arquitetura de Software |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | DESIGN-FOUNDATION-001 |
| Documentos relacionados | PG-001, DOCUMENT_INDEX |

## 1. Objetivo

Definir como documentos controlados são identificados, escritos, revisados, aprovados, versionados e substituídos.

## 2. Estados

| Estado | Significado | Pode orientar implementação? |
|---|---|---|
| Draft | Conteúdo inicial sob elaboração | Apenas exploração e planejamento |
| Review | Conteúdo completo aguardando validação | Com autorização explícita |
| Approved | Conteúdo aceito pelos responsáveis | Sim, antes da baseline formal |
| Baseline | Versão normativa congelada | Sim |
| Superseded | Substituído por versão posterior | Não |

Fluxo: `Draft → Review → Approved → Baseline → Superseded`.

## 3. Versionamento

- `0.1.0`: primeiro draft coerente.
- Incremento minor: mudança de conteúdo ainda não normativo.
- Incremento patch: correção editorial sem mudança de decisão.
- `1.0.0`: primeira baseline aprovada.
- Major posterior: mudança incompatível de decisão ou contrato.

O nome de um documento controlado inclui a versão enquanto estiver antes da baseline. O `DOCUMENT_INDEX.md` é a referência para localizar a versão vigente.

## 4. Metadados obrigatórios

Todo documento controlado começa com:

```markdown
| Campo | Valor |
|---|---|
| Código | PG-001 |
| Título | Product Governance |
| Versão | 0.1.0 |
| Status | Draft |
| Autor | Arquitetura de Software |
| Aprovador | Product Owner |
| Última atualização | 2026-07-14 |
| Dependências | DESIGN-FOUNDATION-001 |
| Documentos relacionados | DOCUMENT_INDEX |
```

Também deve possuir objetivo, escopo, conteúdo, decisões, riscos quando aplicáveis e histórico de alterações.

## 5. Identificadores

- Documento: `<TIPO>-NNN`.
- Requisito funcional: `FR-<DOMÍNIO>-NNN`.
- Requisito não funcional: `NFR-<CATEGORIA>-NNN`.
- Caso de uso: `UC-<DOMÍNIO>-NNN`.
- Teste: `TEST-<ÁREA>-NNN`.
- Evento: nome em inglês no passado, acompanhado de versão.

IDs não são reutilizados. Itens removidos permanecem no histórico como deprecated ou superseded.

## 6. Linguagem e formato

- Português do Brasil para conteúdo de negócio.
- Inglês para nomes técnicos, APIs, código e eventos.
- Markdown UTF-8 e diagramas Mermaid.
- Termos canônicos definidos no PB-001.
- Requisitos escritos de forma testável, sem expressões vagas.
- Datas no formato ISO `YYYY-MM-DD`.

## 7. Aprovação e mudanças

Mudança estrutural exige ADR. Mudança de requisito atualiza PRD/SRS, matriz de rastreabilidade, testes relacionados, índice e changelog. O aprovador não deve ser o único autor de uma decisão de segurança crítica.

## 8. Arquivo morto

`99_Archive` preserva evidências históricas. Conteúdo arquivado nunca é considerado normativo e não deve ser referenciado por implementação nova, salvo para explicar origem de uma decisão.

## 9. Histórico de alterações

| Versão | Data | Alteração |
|---|---|---|
| 0.1.0 | 2026-07-14 | Primeiro padrão documental controlado. |
