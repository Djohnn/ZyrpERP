# Pilot Readiness Checklist

> Use this checklist to verify the environment is ready for a controlled pilot
> in 1–2 stores. Each item must be signed off by the responsible role before
> the pilot can start.

## 1. Tenant & Setup

- [ ] Tenant provisionado com dados reais da loja piloto
- [ ] Usuários operadores criados com perfis corretos
- [ ] Dispositivo PDV registrado e vinculado ao tenant
- [ ] Catálogo de produtos carregado e verificado
- [ ] Estoque inicial registrado (inventário físico)
- [ ] Formas de pagamento configuradas (dinheiro, PIX, cartão débito/crédito)

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 2. PDV Electron

- [ ] PDV Electron instalado no equipamento da loja
- [ ] Login funciona com credenciais da loja
- [ ] Abertura de caixa funcional
- [ ] Venda com dinheiro (com troco) completa o ciclo
- [ ] Venda com PIX completa o ciclo
- [ ] Venda com cartão débito/crédito completa o ciclo
- [ ] Impressão/reimpressão de cupom funciona
- [ ] Fechamento de caixa gera relatório correto
- [ ] Modo offline detecta perda de conectividade
- [ ] Sincronização automática retoma ao voltar online

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 3. Fiscal

- [ ] NFC-e emitida com sucesso para venda teste
- [ ] Webhook de retorno processado
- [ ] Rejeição tratada com reattempt visível no painel
- [ ] Contingência offline armazena para emissão posterior

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 4. Backup & Restore

- [ ] Backup completo do banco executado sem erros
- [ ] Restore em banco descartável verificado
- [ ] Scripts de backup/restore versionados sem segredos embutidos
- [ ] Runbook de backup/restore revisado pela equipe de suporte

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 5. Observabilidade

- [ ] Health/readiness endpoints respondem
- [ ] Dashboard operacional acessível com métricas de API, Outbox, fiscal e PDV
- [ ] Alertas configurados para falha crítica (DB, Redis, fila)
- [ ] Logs estruturados sem exposição de segredos

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 6. Suporte & Incidentes

- [ ] Runbook de incidentes SEV-1 a SEV-4 disponível
- [ ] Runbook de rollback revisado
- [ ] Canais de comunicação definidos (operador → suporte → engenharia)
- [ ] Suporte tem acesso ao ambiente e aos logs

**Responsável:** Suporte \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 7. Segurança & Privacidade

- [ ] Scanner de segredos executado — nenhum credencial versionada
- [ ] RLS verificado por tenant — recursos fora do escopo retornam 404
- [ ] Tokens JWT com expiração curta
- [ ] HTTPS forçado em produção

**Responsável:** Engenharia \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Data: \_\_\_/\_\_\_/\_\_\_\_

## 8. Critérios de Entrada do Piloto

Todos os itens acima devem estar marcados como concluídos.

## 9. Critérios de Saída / Rollback

O piloto será interrompido se qualquer um dos seguintes ocorrer:

- Erro crítico não contornável (perda de dados, falha fiscal sistêmica)
- Sincronização offline falha por mais de 24h sem recuperação
- Violação de isolamento de dados entre tenants
- Incidente de segurança com dados reais de cliente
- Decisão do Product Owner

## Sign-off

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| Produto | | | |
| Engenharia | | | |
| Suporte | | | |
