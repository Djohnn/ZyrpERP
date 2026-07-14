# Fluxo de estados fiscais

**ID:** DIA-005  
**Versão:** 0.1.0  
**Status:** Review

```mermaid
stateDiagram-v2
    [*] --> PENDENTE
    PENDENTE --> ENFILEIRADO: solicitação validada
    ENFILEIRADO --> PROCESSANDO: worker inicia
    PROCESSANDO --> AUTORIZADO: provedor autoriza
    PROCESSANDO --> REJEITADO: rejeição fiscal definitiva
    PROCESSANDO --> AGUARDANDO_RETRY: falha transitória
    AGUARDANDO_RETRY --> ENFILEIRADO: backoff e nova tentativa
    AGUARDANDO_RETRY --> FALHA_TECNICA: tentativas esgotadas
    FALHA_TECNICA --> ENFILEIRADO: reprocessamento auditado
    REJEITADO --> ENFILEIRADO: correção e nova solicitação
    AUTORIZADO --> CANCELAMENTO_PENDENTE: cancelamento solicitado
    CANCELAMENTO_PENDENTE --> CANCELADO: provedor confirma
    CANCELAMENTO_PENDENTE --> AUTORIZADO: cancelamento rejeitado
    AUTORIZADO --> [*]
    CANCELADO --> [*]
```

## Regras

- Cada transição registra ator, instante, correlação, tenant, empresa e filial.
- Reprocessamento reutiliza a identidade lógica da solicitação para evitar emissão duplicada.
- Respostas do provedor são armazenadas de forma sanitizada e auditável.
- Estados internos são independentes da nomenclatura específica de qualquer provedor.

