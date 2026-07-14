# Data Classification

| Classe | Exemplos | Controles mínimos |
|---|---|---|
| Public | documentação pública, status genérico | integridade e revisão |
| Internal | métricas agregadas, runbooks | autenticação e logging |
| Confidential | clientes, vendas, estoque | tenant scope, criptografia e retenção |
| Restricted | certificados, tokens fiscais, credenciais, dados financeiros e documentos fiscais | criptografia de campo, acesso mínimo, auditoria e proibição em logs |

Exportação preserva classificação. Cópias de produção não são usadas em desenvolvimento sem anonimização aprovada.
