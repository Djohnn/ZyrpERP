# Alteração do Fluxo de Impressão de Cupom no PDV — Especificação

**Branch base:** `master`
**Branch de trabalho:** `feat/print-flow-change`

---

## 1. Contexto e Motivação

Atualmente, ao finalizar uma venda no PDV, o sistema abre automaticamente uma tela/modal de impressão, bloqueando o operador até que essa tela seja tratada. Além disso, o botão "Imprimir Cupom Fiscal" hoje **não emite NFC-e de verdade** — apenas adiciona um header "CUPOM FISCAL" a um HTML e imprime. Ou seja, nenhum documento fiscal real é gerado, e o valor dessa venda não alimenta o resumo fiscal do caixa (fechamento de caixa não reflete NFC-e realmente emitidas).

Esta mudança tem dois objetivos combinados:
1. Tornar a impressão do cupom **totalmente opcional e não bloqueante**, via notificação discreta pós-venda.
2. Fazer o botão "Imprimir Cupom Fiscal" disparar a **emissão real da NFC-e** via PlugNotas, de forma assíncrona (outbox), **apenas quando o operador solicitar** — não automaticamente em toda venda.

## 2. Objetivo

Substituir a tela de impressão automática pós-venda por um toast de confirmação não bloqueante, com:
- Impressão imediata do Cupom Balcão (não fiscal) sob demanda.
- Emissão assíncrona (via fila/outbox) da NFC-e **apenas quando o operador solicitar** "Imprimir Cupom Fiscal", sem bloquear o PDV enquanto aguarda a resposta do PlugNotas/SEFAZ.
- Reimpressão a qualquer momento pelo histórico de vendas, incluindo consulta de status de documentos fiscais pendentes.

> **Regra de negócio confirmada:** a NFC-e só é emitida se o operador explicitamente solicitar o Cupom Fiscal. Se o operador optar apenas pelo Cupom Balcão (ou fechar a notificação sem escolher nada), nenhuma NFC-e é emitida para aquela venda.

## 3. Escopo

### Dentro do escopo
- Remoção da abertura automática de tela de impressão após confirmar venda.
- Novo componente de notificação (toast) pós-venda.
- Impressão sob demanda de dois tipos de cupom: **Fiscal** e **Balcão** (não fiscal).
- Reimpressão de qualquer venda via histórico.
- Garantia de que a venda nunca depende da impressão para ser concluída.

### Fora do escopo
- Alterações no fluxo de pagamento, estoque ou caixa.
- Alterações no layout do cupom fiscal em si (apenas disparo de impressão).
- Integração com novos modelos de impressora.

## 4. Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| RF01 | Ao confirmar uma venda com sucesso, o sistema **não** deve abrir nenhuma tela/modal de impressão automaticamente. |
| RF02 | Após a venda, o carrinho deve ser limpo e o estado resetado para uma nova venda imediatamente. |
| RF03 | Um toast de confirmação deve ser exibido com a mensagem "✅ Venda nº {saleNumber} realizada com sucesso." |
| RF04 | O toast deve oferecer os botões: "Imprimir Cupom Fiscal", "Imprimir Cupom Balcão" e "Fechar". |
| RF05 | O botão "Imprimir Cupom Fiscal" deve ficar desabilitado quando não houver configuração fiscal ativa. |
| RF06 | Clicar em "Fechar" apenas oculta o toast, sem nenhum outro efeito colateral. |
| RF07 | Clicar em uma opção de impressão deve disparar a impressão correspondente e ocultar o toast. |
| RF08 | O cupom "Balcão" é um comprovante simplificado, não fiscal, sem dependência de configuração fiscal, e é impresso imediatamente ao ser solicitado (sem chamada externa). |
| RF09 | O histórico de vendas deve permitir reimprimir, a qualquer momento, tanto o Cupom Fiscal (se já autorizado) quanto o Cupom Balcão de uma venda já registrada. |
| RF10 | A reimpressão não deve alterar nenhum dado da venda nem gerar uma nova NFC-e. |
| RF11 | A impressão (inicial ou reimpressão) nunca deve bloquear ou impedir o fluxo normal do PDV. |
| RF12 | Clicar em "Imprimir Cupom Fiscal" **enfileira** a emissão da NFC-e via PlugNotas (job assíncrono) e retorna imediatamente — não aguarda a resposta da SEFAZ/PlugNotas na UI. |
| RF13 | A NFC-e **nunca** é emitida automaticamente na confirmação da venda — apenas quando o operador solicita explicitamente o Cupom Fiscal. |
| RF14 | Enquanto o job de emissão está pendente, o PDV deve indicar isso ao operador (ex: "Emissão em processamento") em vez de imprimir um cupom sem protocolo/chave. |
| RF15 | Quando o job de emissão é autorizado pela SEFAZ, o cupom fiscal impresso (ou reimpresso) deve conter protocolo e chave de acesso da NFC-e. |
| RF16 | Se a emissão for rejeitada, o sistema deve sinalizar o erro fiscal para tratamento (reenvio manual ou correção), sem bloquear o PDV. |
| RF17 | O resumo de caixa continua exibindo o total geral de vendas confirmadas, sem separar visualmente "vendas com fiscal" de "vendas sem fiscal". Internamente, porém, o sistema deve manter o rastreio de quais vendas têm `FiscalDocument` `autorizado`, para permitir consultas/relatórios futuros sem precisar de retrabalho. |

## 5. Requisitos Não Funcionais / Regras de Negócio

- A venda é considerada concluída independentemente de qualquer impressão.
- Se o operador não escolher nenhuma opção de impressão, a venda permanece registrada normalmente, sem documento emitido.
- Toda a lógica de impressão é acionada via IPC (Electron), nunca de forma síncrona/bloqueante na UI.

## 6. Componentes e Arquivos Afetados

### Novo componente
- `pdv/src/renderer/components/SaleConfirmationToast.tsx`
  - **Props:** `saleId`, `saleNumber`, `onClose`, `hasFiscalConfig`
  - **Estilo:** toast fixo (canto inferior direito ou topo), não modal bloqueante.

### Arquivos modificados
- `pdv/src/renderer/pages/Sale.tsx` — remoção da abertura automática da tela de impressão; integração do novo toast pós-finalização.
- `pdv/src/main/ipc/printing.ts` — handler para impressão imediata do Cupom Balcão; handler `requestFiscalReceipt(saleId)` que **enfileira** a emissão (não imprime diretamente).
- `pdv/src/preload/index.ts` — exposição de `printBalcaoReceipt(saleId)`, `requestFiscalReceipt(saleId)` e `getFiscalDocumentStatus(saleId)` via `window.electronAPI`.
- `pdv/src/renderer/utils/receipt.ts` — ajustes auxiliares, se necessário; lógica de exibição conforme status (`pendente` / `autorizado` / `rejeitado`).
- `pdv/src/renderer/pages/Dashboard.tsx` (ou tela de histórico) — adição de "Reimprimir Cupom Fiscal" (habilitado apenas se `autorizado`) e "Reimprimir Cupom Balcão"; exibição de status do documento fiscal por venda.

### Novos itens de backend / worker (fora do processo Electron)
- **Job de emissão de NFC-e**: enfileirado quando o operador solicita o Cupom Fiscal; consome a fila, chama PlugNotas, atualiza status.
- **Modelo `FiscalDocument`** (ou equivalente): `saleId`, `status` (`pendente` | `autorizado` | `rejeitado`), `protocolo`, `chaveAcesso`, `solicitadoEm`, `respondidoEm`, `motivoRejeicao`.
- **Resumo de caixa**: o total exibido no fechamento **não muda** (continua sendo o total geral de vendas confirmadas). O sistema passa a manter, internamente, o vínculo entre `saleId` e status do `FiscalDocument`, sem exibir essa separação no relatório atual — serve de base para relatórios/consultas futuras sobre vendas com fiscal emitido.

## 7. Fluxo Proposto

1. Operador finaliza a venda (pagamentos processados, estoque/caixa atualizados). **Nenhuma NFC-e é emitida neste momento.**
2. Sistema limpa o carrinho e reseta o estado para nova venda.
3. Toast de confirmação é exibido com os dados da venda.
4. Operador escolhe:
   - **Fechar** → toast desaparece, nada mais acontece. Nenhuma NFC-e será emitida para esta venda.
   - **Imprimir Cupom Balcão** → dispara `printBalcaoReceipt(saleId)` via IPC, imprime imediatamente, toast desaparece.
   - **Imprimir Cupom Fiscal** → dispara `requestFiscalReceipt(saleId)` via IPC, que **enfileira** o job de emissão e retorna na hora (não bloqueia); toast pode fechar imediatamente ou mostrar "Emissão em processamento", conforme decisão de UX.
5. Em background, um worker consome a fila, chama o PlugNotas e atualiza o `FiscalDocument` da venda para `autorizado` (com protocolo/chave) ou `rejeitado` (com motivo).
6. Quando autorizado, o cupom fiscal fica disponível para impressão (automática, se o PDV ainda estiver na tela, ou via histórico).
7. A qualquer momento, no histórico de vendas, o operador pode:
   - Reimprimir o Cupom Balcão livremente.
   - Reimprimir o Cupom Fiscal **apenas se** o `FiscalDocument` estiver `autorizado`.
   - Ver o status de um documento fiscal pendente ou rejeitado.

> **Confirmado:** se uma venda nunca teve o Cupom Fiscal solicitado (operador só imprimiu o Balcão ou fechou o toast), o histórico **deve permitir solicitar a emissão da NFC-e retroativamente**, a qualquer momento. Isso implica que a Task 5 (histórico) precisa de uma ação "Solicitar Cupom Fiscal" — não apenas "Reimprimir" — para vendas cujo `FiscalDocument` ainda não existe.

## 8. Interface (API interna / IPC)

```ts
window.electronAPI.printBalcaoReceipt(saleId: string): Promise<void>
window.electronAPI.requestFiscalReceipt(saleId: string): Promise<{ status: "pendente" | "autorizado" | "rejeitado" }>
window.electronAPI.getFiscalDocumentStatus(saleId: string): Promise<{
  status: "pendente" | "autorizado" | "rejeitado";
  protocolo?: string;
  chaveAcesso?: string;
  motivoRejeicao?: string;
}>
```

- `printBalcaoReceipt` imprime diretamente, sem dependência externa.
- `requestFiscalReceipt` apenas enfileira o job (não aguarda PlugNotas) e retorna o status inicial (`pendente`), ou o status já existente se já foi solicitado antes.
- `getFiscalDocumentStatus` é usado pelo histórico e pela UI para saber se já é possível reimprimir o fiscal.
- O botão "Imprimir Cupom Fiscal" na notificação continua desabilitado se não houver configuração fiscal ativa (`hasFiscalConfig`).

## 9. Critérios de Aceite

- [ ] Nenhuma tela de impressão abre automaticamente após confirmar venda.
- [ ] Nenhuma NFC-e é emitida automaticamente na confirmação da venda.
- [ ] Toast exibe corretamente número da venda e opções.
- [ ] Botão fiscal desabilitado quando não há config fiscal.
- [ ] "Fechar" não dispara impressão nem emissão fiscal.
- [ ] "Imprimir Cupom Fiscal" enfileira a emissão e retorna sem travar a UI (sem esperar resposta do PlugNotas/SEFAZ).
- [ ] Cupom fiscal impresso (inicial ou reimpressão) sempre contém protocolo/chave — nunca é impresso um cupom fiscal "vazio" (sem NFC-e autorizada).
- [ ] Reimpressão do Balcão funcional a partir do histórico, sem alterar a venda.
- [ ] Reimpressão do Fiscal só é permitida quando o `FiscalDocument` estiver `autorizado`.
- [ ] Resumo de caixa continua exibindo o total geral, sem separação visual fiscal x não fiscal, mas o vínculo `saleId` ↔ status do `FiscalDocument` é rastreável internamente.
- [ ] Impressão nunca bloqueia o fluxo do PDV (venda sempre é considerada concluída antes/independente da impressão ou emissão).

## 10. Testes

| Arquivo | Cobertura |
|---------|-----------|
| `pdv/src/renderer/__tests__/pages/Sale.test.tsx` | Venda finalizada não abre impressão automática nem dispara emissão fiscal |
| `pdv/src/renderer/__tests__/components/SaleConfirmationToast.test.tsx` | Dados corretos exibidos; botão fiscal desabilitado sem config; "Fechar" apenas oculta; solicitar fiscal não bloqueia UI |
| `pdv/src/renderer/__tests__/pages/Dashboard.test.tsx` | Reimpressão de Balcão livre; reimpressão de Fiscal bloqueada se não autorizado; exibição de status pendente/rejeitado |
| *(backend/worker, fora do escopo do PDV renderer)* | Job de emissão: transições de status `pendente` → `autorizado`/`rejeitado`; resumo de caixa considera apenas `autorizado` |

## 11. Verificação Final

- Rodar `npx vitest run` no PDV.
- Aceitar as 11 falhas pré-existentes do `better-sqlite3`; nenhuma falha nova pode ser introduzida.
- Commit final: `feat: alteração fluxo impressão cupom PDV - impressão opcional pós-venda`
