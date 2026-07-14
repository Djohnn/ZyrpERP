# ADR-001 — Monólito modular Django

| Campo | Valor |
|---|---|
| Status | Accepted |
| Data | 2026-07-14 |

## Contexto
O MVP reúne capacidades comerciais fortemente relacionadas, enquanto a equipe e a operação ainda precisam validar produto e escala.

## Forças
Velocidade, consistência transacional, baixo custo operacional, fronteiras evolutivas e testabilidade.

## Opções
1. Monólito modular Django. 2. Microsserviços. 3. Monólito sem fronteiras.

## Decisão
Adotar monólito modular Django, com módulos por capability, serviços públicos explícitos, eventos internos e proibição de HTTP entre módulos.

## Consequências positivas
- Deploy e observabilidade iniciais simples.
- Transações locais confiáveis.
- Possibilidade de extração futura por fronteira.

## Consequências negativas
- Escalabilidade é inicialmente conjunta.
- Disciplina arquitetural depende de testes e revisão.
- Falhas podem afetar uma unidade de deploy maior.

## Riscos
Acoplamento indevido e modelo compartilhado informal.

## Mitigações
Testes de dependência, contracts, ownership por módulo e revisão periódica.

## Critérios de revisão
Reavaliar quando uma capability exigir escala, disponibilidade, tecnologia ou cadência de release independentes.

