# ADR-004 — Provedor fiscal externo pago pelo cliente

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
Integração direta nacional demanda equipe fiscal, atualização contínua e grande responsabilidade operacional.

## Forças
Prazo, conformidade, custo previsível, substituição e experiência do cliente.

## Opções
1. Provedor externo por cliente. 2. Conta central da plataforma. 3. Integração direta SEFAZ.

## Decisão
Cada cliente contrata provedor e certificado. O ERP usa `FiscalProvider` e um adapter inicial escolhido por ADR futuro.

## Consequências positivas
- Custo fiscal não é subsidiado no MVP.
- Menor tempo de lançamento.
- Provedor substituível.

## Consequências negativas
- Onboarding inclui contrato externo.
- Suporte depende de terceiro.
- Experiência e preço variam por provedor.

## Riscos
Lock-in, indisponibilidade, divergência de contrato e tratamento inseguro de credenciais.

## Mitigações
Port/adapter, homologação, circuit breaker, criptografia e armazenamento próprio de XML/protocolos.

## Critérios de revisão
Reavaliar conta central ou integração própria após volume e unit economics comprovados.

