# ADR-005 — IA como capability futura

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
IA pode apoiar consulta, reposição e documentação, mas não é necessária para validar o ERP.

## Forças
Foco, custo, privacidade, segurança e reversibilidade tecnológica.

## Opções
1. Preparar contratos e adiar IA. 2. IA no MVP. 3. Ignorar preparação.

## Decisão
IA fica fora do MVP. APIs, eventos, auditoria, documentos e permissões permitirão RAG e agentes futuros sem acesso direto irrestrito ao banco.

## Consequências positivas
- MVP determinístico e independente de modelos.
- Dados históricos de melhor qualidade no futuro.
- Modelos e frameworks substituíveis.

## Consequências negativas
- Valor de IA é adiado.
- Preparação exige disciplina de metadados.
- APIs podem precisar evoluir para ferramentas de agente.

## Riscos
Vazamento cross-tenant, alucinação e ação indevida.

## Mitigações
Retrieval filtrado, tools autorizadas, aprovação humana, auditoria, avaliação e limites de custo.

## Critérios de revisão
Iniciar por RAG documental e copiloto somente leitura após Core estável e corpus autorizado.

