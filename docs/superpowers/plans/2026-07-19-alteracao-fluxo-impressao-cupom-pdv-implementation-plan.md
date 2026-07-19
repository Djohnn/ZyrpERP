# Alteração do Fluxo de Impressão de Cupom no PDV — Plano de Implementação

> **Base branch:** `master` (Sprint 8 acabou de ser commitada em branch separada)
> **Nova branch:** `feat/print-flow-change`

---

## Task 1: Remover abertura automática da tela de impressão

**Arquivos:**
- Modificar: `pdv/src/renderer/pages/Sale.tsx`

- [ ] Localizar o handler de "Confirmar Venda" (finalização).
- [ ] Remover qualquer chamada que abra modal/print screen automaticamente após sucesso.
- [ ] Após salvar venda + pagamentos + atualizar estoque/caixa:
  - Limpar carrinho
  - Resetar estado para nova venda
  - Não abrir nenhuma tela de impressão

---

## Task 2: Criar componente de notificação pós-venda

**Arquivos:**
- Criar: `pdv/src/renderer/components/SaleConfirmationToast.tsx`

- [ ] Componente de notificação discreta com:
  - Mensagem: "✅ Venda nº {saleNumber} realizada com sucesso."
  - Botão "Imprimir Cupom Fiscal" (desabilitado se sem config fiscal ativa)
  - Botão "Imprimir Cupom Balcão"
  - Botão "Fechar" (apenas fecha a notificação)
- [ ] Estilo: toast fixo no canto inferior direito ou topo, não modal bloqueante
- [ ] Props: `saleId`, `saleNumber`, `onClose`, `hasFiscalConfig`

---

## Task 3: Integrar notificação no fluxo de venda

**Arquivos:**
- Modificar: `pdv/src/renderer/pages/Sale.tsx`

- [ ] Após finalização bem-sucedida, exibir `SaleConfirmationToast` com dados da venda.
- [ ] Estado do carrinho já limpo, sistema pronto para nova venda.
- [ ] Se operador clicar "Fechar" → apenas esconde o toast.
- [ ] Se operador clicar em opção de impressão → disparar print e esconder toast.

---

## Task 4: Implementar impressão de Cupom Fiscal e Cupom Balcão

**Arquivos:**
- Modificar: `pdv/src/main/ipc/printing.ts`
- Modificar: `pdv/src/preload/index.ts`
- Modificar: `pdv/src/renderer/utils/receipt.ts` (se necessário)

- [ ] **Cupom Fiscal**: disparar impressão via `window.electronAPI.printFiscalReceipt(saleId)` → IPC handler no main process.
  - Verificar se há configuração fiscal ativa antes.
  - Se não houver, botão desabilitado na notificação.
- [ ] **Cupom Balcão**: disparar impressão via `window.electronAPI.printBalcaoReceipt(saleId)` → IPC handler no main process.
  - Cupom simplificado, sem dependência fiscal.
  - Layout estilo "comprovante não fiscal".
- [ ] IPC handlers em `printing.ts` com `pageSize` correto (objeto `{ width, height }`).
- [ ] Expor `printFiscalReceipt` e `printBalcaoReceipt` no preload.

---

## Task 5: Adicionar reimpressão no histórico de vendas

**Arquivos:**
- Modificar: `pdv/src/renderer/pages/Dashboard.tsx` (ou tela de histórico)

- [ ] No menu de ações (3-dots) de cada venda, adicionar:
  - "Reimprimir Cupom Fiscal"
  - "Reimprimir Cupom Balcão"
- [ ] Reimpressão usa mesmos handlers IPC de impressão.
- [ ] Nenhuma alteração na venda é necessária.

---

## Task 6: Regras de negócio — validações

- [ ] Venda nunca depende de impressão para ser concluída.
- [ ] Impressão é totalmente opcional.
- [ ] Se operador não escolher opção, venda permanece registrada sem documento.
- [ ] Histórico permite reimpressão a qualquer momento.
- [ ] Impressão nunca bloqueia fluxo do PDV.

---

## Task 7: Testes

**Arquivos:**
- Modificar: `pdv/src/renderer/__tests__/pages/Sale.test.tsx`
- Criar: `pdv/src/renderer/__tests__/components/SaleConfirmationToast.test.tsx`
- Modificar: `pdv/src/renderer/__tests__/pages/Dashboard.test.tsx`

- [ ] Testar que venda finalizada não abre tela de impressão automaticamente.
- [ ] Testar que `SaleConfirmationToast` exibe dados corretos.
- [ ] Testar que botão "Imprimir Cupom Fiscal" está desabilitado sem config fiscal.
- [ ] Testar que "Fechar" apenas esconde toast.
- [ ] Testar reimpressão no histórico de vendas.

---

## Task 8: Verificação

- [ ] Rodar `npx vitest run` no PDV.
- [ ] Verificar que 0 novas falhas foram introduzidas (11 falhas pré-existentes do `better-sqlite3` são aceitas).
- [ ] Commit: `feat: alteração fluxo impressão cupom PDV - impressão opcional pós-venda`
