# Sequência de sincronização do PDV

**ID:** DIA-004  
**Versão:** 0.1.0  
**Status:** Review

```mermaid
sequenceDiagram
    autonumber
    actor Operador
    participant PDV as PDV Electron
    participant Local as SQLite local
    participant API as API Django
    participant DB as PostgreSQL
    participant Outbox as Transactional Outbox

    Operador->>PDV: Finaliza venda
    alt API disponível
        PDV->>API: POST /sales + Idempotency-Key
        API->>DB: valida tenant, filial, estoque e versão
        API->>DB: persiste venda e movimentos
        API->>Outbox: registra eventos na mesma transação
        API-->>PDV: 201 + identificador + versão
        PDV->>Local: registra confirmação central
    else indisponibilidade elegível para contingência
        PDV->>Local: persiste venda pendente e chave idempotente
        PDV-->>Operador: confirma contingência restrita
        loop até reconectar
            PDV->>API: envia pendência + Idempotency-Key
            API->>DB: valida e reconcilia
            alt aceita
                API-->>PDV: confirmação e versão central
                PDV->>Local: marca sincronizada
            else conflito ou rejeição
                API-->>PDV: problem+json + código do conflito
                PDV->>Local: marca para intervenção auditada
            end
        end
    end
```

## Garantias

- Toda tentativa reutiliza a mesma chave de idempotência.
- O modo offline permite apenas operações essenciais previamente autorizadas.
- Conflitos não são descartados silenciosamente e exigem trilha de auditoria.
- Emissão fiscal offline segue as capacidades e regras do provedor contratado.

