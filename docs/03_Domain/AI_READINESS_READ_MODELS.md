# AI Readiness — Read Models Permitidos

## Princípio

Qualquer RAG ou copiloto futuro opera exclusivamente em modo de leitura. Nenhum fluxo de IA
pode criar, alterar, liquidar, cancelar ou excluir fatos de vendas, estoque, fiscal ou financeiro.
Ações transacionais futuras exigem workflow separado, autorização explícita e aprovação humana.

## Fontes permitidas

| Read model | Uso permitido | Restrições |
|---|---|---|
| Vendas agregadas | totais por período/filial | sem dados pessoais ou payload de pagamento |
| Fechamento de caixa | totais e divergências agregadas | sem credenciais ou identificação desnecessária do operador |
| Estoque | SKU, quantidade, reservado e crítico | sempre tenant/filial scoped |
| Financeiro | saldos agregados por status e vencimento | valores detalhados são `Restricted` |
| Fluxo de caixa | realizado, previsto e saldo agregado | sem conta bancária, token ou segredo de provider |
| Pendências fiscais/Outbox | contagens por status | sem XML, certificado, token ou payload bruto |

## Fontes proibidas

- Segredos, tokens, certificados, chaves privadas e credenciais de providers.
- XML/PDF fiscal bruto, payload de webhook ou evento Outbox completo.
- CPF/CNPJ, endereço, contato ou documento pessoal sem redaction e base legal aprovada.
- Dados cross-tenant ou consultas sem tenant ativo validado.

## Controles obrigatórios

- Autorização idêntica à API de origem e filtro tenant-scoped no servidor.
- Citações das fontes utilizadas, auditoria da consulta e correlação de requisição.
- Exportações limitadas a 1.000 linhas e sem campos classificados como segredo.
- Respostas somente leitura; nenhuma ferramenta transacional fica disponível ao modelo.
