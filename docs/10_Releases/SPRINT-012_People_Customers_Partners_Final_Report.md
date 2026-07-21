# Sprint 12 — Pessoas, Clientes e Parceiros — Relatório Final

## Status

Concluída em 2026-07-21.

## Entregas

- App `people` tenant-scoped com PF/PJ, papéis, documentos, endereços, contatos e consentimentos.
- Normalização de CPF/CNPJ, CEP, telefone e e-mail, com unicidade de documento ativo por tenant.
- Criação e desativação lógica com auditoria e Outbox sem dados pessoais brutos.
- APIs CRUD, filtros, desativação e recursos aninhados, incluindo proteção cross-tenant.
- Cliente opcional em vendas, vínculo de fornecedor com pessoa e destinatário fiscal normalizado.

## Cenários BDD automatizados

- Given dados PF/PJ brutos, when persistidos, then identificadores são normalizados.
- Given documento ativo, when repetido, then somente o mesmo tenant é bloqueado.
- Given dados pessoais, when eventos são emitidos, then PII não aparece no payload.
- Given pessoa de outro tenant, when consultada pela API, then a resposta é 404.
- Given venda de balcão, when nenhum cliente é informado, then o fluxo anônimo permanece válido.

## Evidências

### Suíte focada

```text
10 passed in 12.67s
people coverage: 95.00%
```

### Suíte completa

```text
406 passed in 179.89s (0:02:59)
Required test coverage of 80% reached. Total coverage: 81.72%
```

### Qualidade estática e Django

```text
All checks passed!
Success: no issues found in 212 source files
System check identified no issues (0 silenced).
No changes detected
```

## Aceite

Todos os critérios funcionais e de qualidade definidos para a Sprint 12 foram atendidos.
