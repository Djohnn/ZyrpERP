# Data Classification

| Classe | Exemplos | Controles mínimos |
|---|---|---|
| Public | documentação pública, status genérico | integridade e revisão |
| Internal | métricas agregadas, runbooks | autenticação e logging |
| Confidential | clientes, vendas, estoque | tenant scope, criptografia e retenção |
| Restricted | certificados, tokens fiscais, credenciais, dados financeiros e documentos fiscais | criptografia de campo, acesso mínimo, auditoria e proibição em logs |

Exportação preserva classificação. Cópias de produção não são usadas em desenvolvimento sem anonimização aprovada.

## Financeiro, fiscal e IA

| Campo ou artefato | Classe | Uso por IA |
|---|---|---|
| Totais agregados de vendas/estoque | Confidential | permitido em read model tenant-scoped |
| Valor, vencimento, liquidação e fluxo de caixa | Restricted | somente agregado e autorizado |
| CPF/CNPJ, destinatário e endereço fiscal | Restricted | proibido sem redaction/base legal |
| XML/PDF fiscal e payload de webhook | Restricted | proibido |
| Token, certificado, chave e segredo de provider | Restricted | sempre proibido |

Copilotos futuros permanecem somente leitura. Escritas financeiras, fiscais, comerciais ou de
estoque exigem aprovação humana e workflow transacional fora do contexto do modelo.
