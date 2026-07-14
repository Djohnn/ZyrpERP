# Threat Model — STRIDE

| Ameaça | Categoria | Preventivo | Detectivo | Resposta |
|---|---|---|---|---|
| Acesso cross-tenant/IDOR | Spoofing/Elevation | autorização contextual + RLS | teste e alerta de policy | bloquear, investigar e notificar |
| Replay de webhook | Tampering | assinatura, timestamp e nonce | duplicidade por event ID | rejeitar e rotacionar segredo |
| Exfiltração de certificado | Disclosure | envelope encryption e least privilege | acesso auditado e DLP | revogar, substituir e investigar |
| PDV roubado | Spoofing/Disclosure | disco criptografado e token curto | heartbeat e anomalia | revogar dispositivo e sessão |
| Evento/Outbox adulterado | Tampering | DB ACL e integridade | reconciliação e hash | pausar consumidor e replay seguro |
| Elevação de privilégio | Elevation | RBAC contextual e MFA | auditoria de grants | revogar e revisar impacto |
| Backup exposto | Disclosure | criptografia e storage privado | monitoramento de acesso | revogar chaves e incidente LGPD |
| Negação de serviço fiscal | DoS | timeout, circuit breaker e fila | métricas e alerta | contingência e comunicação |

Risco residual crítico exige aceite formal do Security Owner e Product Owner antes de produção.

