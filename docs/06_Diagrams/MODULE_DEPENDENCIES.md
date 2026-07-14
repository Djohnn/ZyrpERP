# Dependências entre módulos

**ID:** DIA-003  
**Versão:** 0.1.0  
**Status:** Review

```mermaid
flowchart LR
    iam["IAM e permissões"]
    tenancy["Tenancy e organizações"]
    catalogo["Catálogo"]
    estoque["Estoque"]
    vendas["Vendas"]
    pdv["PDV e caixa"]
    fiscal["Fiscal"]
    financeiro["Financeiro"]
    integracoes["Integrações"]
    auditoria["Auditoria e observabilidade"]
    ia["Capacidades de IA futuras"]

    iam --> tenancy
    tenancy --> catalogo
    catalogo --> estoque
    catalogo --> vendas
    estoque --> vendas
    vendas --> pdv
    pdv --> fiscal
    vendas --> financeiro
    fiscal --> integracoes
    financeiro --> integracoes

    iam -.-> auditoria
    tenancy -.-> auditoria
    vendas -.-> auditoria
    fiscal -.-> auditoria

    auditoria -."eventos e dados autorizados".-> ia
    catalogo -."APIs autorizadas".-> ia
    vendas -."APIs autorizadas".-> ia
```

## Restrições

- Dependências seguem contratos públicos de aplicação; módulos não leem tabelas privadas de outros módulos.
- Fiscal depende de vendas concluídas, mas vendas não depende de detalhes de um provedor fiscal.
- IA futura consome APIs, eventos e bases autorizadas; não recebe acesso irrestrito ao banco.

