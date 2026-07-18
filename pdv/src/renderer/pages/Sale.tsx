import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCashSession } from '../contexts/CashSessionContext';
import { Card, Button, Input, Modal } from '../components/ui';

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('access_token');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const tid = localStorage.getItem('tenant_id');
  if (tid) headers['X-Tenant-ID'] = tid;
  return headers;
}

export function Sale() {
  const { isAuthenticated } = useAuth();
  const { session } = useCashSession();
  const navigate = useNavigate();

  const [items, setItems] = useState<Array<{
    product: any;
    quantity: number;
    factor: number;
    unitPrice: number;
    discount: number;
    lineTotal: number;
  }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSearch, setShowSearch] = useState(false);
  const [payments, setPayments] = useState<Array<{ method: string; amount: number; reference: string }>>([]);
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'pix' | 'card' | 'card_integrated'>('cash');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentReference, setPaymentReference] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [receipt, setReceipt] = useState<any>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const calculateTotals = useCallback(() => {
    const grossTotal = items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
    const discountTotal = items.reduce((sum, item) => sum + item.discount, 0);
    const netTotal = grossTotal - discountTotal;
    const paymentTotal = payments.reduce((sum, p) => sum + p.amount, 0);
    return { grossTotal, discountTotal, netTotal, paymentTotal };
  }, [items, payments]);

  const { grossTotal, discountTotal, netTotal, paymentTotal } = calculateTotals();
  const changeAmount = paymentTotal - netTotal;

  const handleProductSelect = (product: any) => {
    setShowSearch(false);
    setSearchQuery('');
    setSearchResults([]);
    const unitPrice = Number(product.price ?? 0);

    const existingIndex = items.findIndex(item => item.product.id === product.id);
    if (existingIndex >= 0) {
      setItems(prev => {
        const newItems = [...prev];
        newItems[existingIndex] = {
          ...newItems[existingIndex],
          quantity: newItems[existingIndex].quantity + 1,
          lineTotal: (newItems[existingIndex].quantity + 1) * newItems[existingIndex].unitPrice - newItems[existingIndex].discount
        };
        return newItems;
      });
    } else {
      setItems(prev => [...prev, {
        product,
        quantity: 1,
        factor: 1,
        unitPrice,
        discount: 0,
        lineTotal: unitPrice,
      }]);
    }
  };

  const handleSearchChange = async (query: string) => {
    setSearchQuery(query);
    if (query.length >= 2) {
      try {
        const response = await fetch(`/api/v1/products/?search=${encodeURIComponent(query)}`, {
          headers: authHeaders()
        });
        if (response.ok) {
          const data = await response.json();
          setSearchResults(data.results || data);
        }
      } catch (e) {
        console.error('Search error:', e);
      }
      setShowSearch(true);
    } else {
      setSearchResults([]);
      setShowSearch(false);
    }
  };

  const updateItemQuantity = (index: number, quantity: number) => {
    if (quantity <= 0) {
      setItems(prev => prev.filter((_, i) => i !== index));
      return;
    }
    setItems(prev => {
      const newItems = [...prev];
      newItems[index] = {
        ...newItems[index],
        quantity,
        lineTotal: quantity * newItems[index].unitPrice - newItems[index].discount
      };
      return newItems;
    });
  };

  const updateItemDiscount = (index: number, discount: number) => {
    setItems(prev => {
      const newItems = [...prev];
      const item = newItems[index];
      const lineTotal = item.quantity * item.unitPrice - discount;
      if (lineTotal < 0) return prev;
      newItems[index] = { ...item, discount, lineTotal };
      return newItems;
    });
  };

  const removeItem = (index: number) => {
    setItems(prev => prev.filter((_, i) => i !== index));
  };

  const addPayment = () => {
    if (!paymentAmount || parseFloat(paymentAmount) <= 0) return;
    setPayments(prev => [...prev, {
      method: paymentMethod,
      amount: parseFloat(paymentAmount),
      reference: paymentReference
    }]);
    setPaymentAmount('');
    setPaymentReference('');
  };

  const removePayment = (index: number) => {
    setPayments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (items.length === 0) {
      setError('Adicione pelo menos um item à venda');
      return;
    }
    if (payments.length === 0) {
      setError('Adicione pelo menos um pagamento');
      return;
    }
    if (paymentTotal < parseFloat(netTotal.toFixed(2))) {
      setError(`Pagamento insuficiente. Faltam ${(parseFloat(netTotal.toFixed(2)) - paymentTotal).toFixed(2)}`);
      return;
    }
    if (!session.sessionId) {
      setError('Nenhum caixa aberto. Abra o caixa primeiro.');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const itemsPayload = items.map(item => ({
        product: item.product.id,
        unit: typeof item.product.base_unit === 'object' ? item.product.base_unit?.id : item.product.base_unit,
        quantity: item.quantity.toString(),
        factor: item.factor.toString(),
        discount_amount: item.discount.toFixed(2)
      }));

      const paymentsPayload = payments.map(p => ({
        method: p.method,
        amount: p.amount.toFixed(2),
        reference: p.reference || undefined
      }));

      const response = await fetch('/api/v1/sales/counter/', {
        method: 'POST',
        headers: { ...authHeaders(), 'Idempotency-Key': crypto.randomUUID() },
        body: JSON.stringify({
          branch: localStorage.getItem('branch_id'),
          stock_location: localStorage.getItem('stock_location_id'),
          items: itemsPayload,
          payments: paymentsPayload,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Erro ao criar venda');
      }

      const sale = await response.json();
      const receiptItems = sale.items?.map((saleItem: any) => {
        const cartItem = items.find(item => item.product.id === saleItem.product);
        return {
          ...saleItem,
          product: cartItem?.product || saleItem.product,
        };
      });
      setReceipt({ ...sale, items: receiptItems || sale.items });
      setItems([]);
      setPayments([]);
      setError('');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro ao processar venda');
    } finally {
      setProcessing(false);
    }
  };

  if (!isAuthenticated) return null;

  const formatReceiptQuantity = (quantity: string | number): string => {
    const value = Number(quantity);
    if (!Number.isFinite(value)) return String(quantity);
    return value.toFixed(1);
  };

  const handlePrintReceipt = () => {
    window.print();
  };

  return (
    <div style={{ display: 'flex', height: '100vh', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        background: '#fff', borderBottom: '1px solid #e0e0e0', padding: '16px 24px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#1976d2' }}>Zyrp PDV</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginLeft: '24px', paddingLeft: '24px', borderLeft: '1px solid #e0e0e0' }}>
            <span style={{ fontSize: '0.875rem', color: '#757575' }}>Caixa: </span>
            <strong>{session.status === 'open' ? 'ABERTO' : 'FECHADO'}</strong>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '0.875rem', color: '#757575' }}>
            {localStorage.getItem('branch_id') ? `Filial: ${localStorage.getItem('branch_id')}` : ''}
          </span>
          {session.status === 'open' && (
            <Link to="/cash-session">
              <Button variant="danger">Fechar Caixa</Button>
            </Link>
          )}
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>Dashboard</Button>
        </div>
      </header>

      <main style={{ flex: 1, padding: '24px', overflow: 'auto' }}>
        {error && (
          <div style={{
            background: '#fce4ec', border: '1px solid #ef9a9a', borderRadius: '8px',
            padding: '16px', marginBottom: '24px', display: 'flex',
            justifyContent: 'space-between', alignItems: 'center'
          }}>
            <span style={{ color: '#c62828' }}>{error}</span>
            <button onClick={() => setError('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#c62828', fontSize: '1.25rem' }}>x</button>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '24px', height: 'calc(100vh - 200px)', minHeight: '600px' }}>
          {/* Left Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Product Search */}
            <Card style={{ padding: '24px', position: 'relative' }}>
              <h3 style={{ marginBottom: '16px', fontSize: '1rem', fontWeight: 600 }}>Adicionar Produtos</h3>
              <Input
                placeholder="Buscar produto (SKU ou nome)..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
              />
              {showSearch && searchResults.length > 0 && (
                <div style={{
                  position: 'absolute', zIndex: 10, left: '24px', right: '24px',
                  background: '#fff', border: '1px solid #e0e0e0', borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)', maxHeight: '300px', overflowY: 'auto'
                }}>
                  {searchResults.slice(0, 10).map((product: any) => (
                    <div key={product.id} onClick={() => handleProductSelect(product)}
                      style={{ padding: '12px 16px', cursor: 'pointer', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>{product.name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#757575' }}>SKU: {product.sku}</div>
                      </div>
                      <div style={{ fontWeight: 600, color: '#1976d2', fontSize: '0.875rem' }}>
                        {product.price ? `R$ ${parseFloat(product.price).toFixed(2)}` : 'Sem preço'}
                      </div>
                    </div>
                  ))}
                  {searchResults.length > 10 && (
                    <div style={{ padding: '12px', textAlign: 'center', color: '#757575', fontSize: '0.875rem' }}>
                      Mostrando 10 de {searchResults.length} resultados
                    </div>
                  )}
                </div>
              )}
            </Card>

            {/* Cart */}
            <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Carrinho ({items.length})</h3>
                {items.length > 0 && (
                  <Button variant="secondary" size="sm" onClick={() => setItems([])}>Limpar</Button>
                )}
              </div>

              {items.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '48px 24px', color: '#757575' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem' }}>Carrinho vazio</p>
                  <p style={{ margin: '8px 0 0', fontSize: '0.75rem', color: '#9e9e9e' }}>Busque e adicione produtos acima</p>
                </div>
              ) : (
                <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
                  {items.map((item, index) => (
                    <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 500, fontSize: '0.875rem', marginBottom: '4px' }}>{item.product.name}</div>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                          <span style={{ fontSize: '0.75rem', color: '#757575' }}>Qtd:</span>
                          <input type="number" min="1" value={item.quantity}
                            onChange={(e) => updateItemQuantity(index, parseInt(e.target.value) || 1)}
                            style={{ width: '60px', padding: '4px 8px', fontSize: '0.875rem' }} />
                          <span style={{ fontSize: '0.75rem', color: '#757575' }}>Desc:</span>
                          <input type="number" min="0" step="0.01" value={item.discount.toFixed(2)}
                            onChange={(e) => updateItemDiscount(index, parseFloat(e.target.value) || 0)}
                            style={{ width: '80px', padding: '4px 8px', fontSize: '0.875rem' }} />
                        </div>
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#1976d2', whiteSpace: 'nowrap' }}>
                        R$ {item.lineTotal.toFixed(2)}
                      </div>
                      <button onClick={() => removeItem(index)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#c62828', padding: '4px' }}>
                        X
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Right Panel - Payment */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <Card style={{ padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', fontSize: '1rem', fontWeight: 600 }}>Pagamento</h3>

              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
                {['cash', 'pix', 'card_external', 'card_integrated'].map(method => (
                  <label key={method} style={{
                    display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px',
                    border: `2px solid ${paymentMethod === method ? '#1976d2' : '#e0e0e0'}`,
                    borderRadius: '8px', cursor: 'pointer',
                    background: paymentMethod === method ? '#e3f2fd' : '#fff',
                    transition: 'all 0.2s'
                  }}>
                    <input type="radio" name="paymentMethod" value={method}
                      checked={paymentMethod === method}
                      onChange={() => setPaymentMethod(method as any)}
                      style={{ display: 'none' }} />
                    <span style={{ fontWeight: 500, textTransform: 'capitalize', color: paymentMethod === method ? '#1976d2' : '#333' }}>
                      {method === 'cash' && 'Dinheiro'}
                      {method === 'pix' && 'PIX'}
                      {method === 'card_external' && 'Cartão (TEF)'}
                      {method === 'card_integrated' && 'Cartão (integrado)'}
                    </span>
                  </label>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: '#757575', marginBottom: '4px' }}>Valor</label>
                  <input type="number" step="0.01" min="0.01" value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)} placeholder="0,00"
                    style={{ width: '100%', padding: '12px 16px', fontSize: '1rem', border: '1px solid #e0e0e0', borderRadius: '8px' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: '#757575', marginBottom: '4px' }}>Referência</label>
                  <input type="text" value={paymentReference}
                    onChange={(e) => setPaymentReference(e.target.value)} placeholder="Opcional"
                    style={{ width: '100%', padding: '12px 16px', border: '1px solid #e0e0e0', borderRadius: '8px', fontSize: '1rem' }} />
                </div>
              </div>

              <Button variant="primary" fullWidth onClick={addPayment}
                disabled={!paymentAmount || parseFloat(paymentAmount) <= 0}>
                Adicionar Pagamento
              </Button>

              {payments.length > 0 && (
                <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #f0f0f0' }}>
                  <h4 style={{ margin: '0 0 12px', fontSize: '0.875rem', fontWeight: 600 }}>Pagamentos</h4>
                  {payments.map((payment, index) => (
                    <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#fafafa', borderRadius: '8px', marginBottom: '8px' }}>
                      <div>
                        <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>{payment.method}</div>
                        {payment.reference && <div style={{ fontSize: '0.75rem', color: '#757575' }}>Ref: {payment.reference}</div>}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontWeight: 600, color: '#1976d2' }}>R$ {payment.amount.toFixed(2)}</span>
                        <button onClick={() => removePayment(index)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#c62828' }}>X</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Totals */}
            <Card style={{ padding: '24px', background: '#f5f5f5' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#757575' }}>Subtotal</span>
                  <span style={{ fontWeight: 500 }}>R$ {grossTotal.toFixed(2)}</span>
                </div>
                {discountTotal > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#c62828' }}>
                    <span>Desconto</span>
                    <span style={{ fontWeight: 500 }}>-R$ {discountTotal.toFixed(2)}</span>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #e0e0e0', paddingTop: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '1.125rem', fontWeight: 600 }}>Total</span>
                  <span style={{ fontSize: '1.125rem', fontWeight: 700, color: '#1976d2' }}>R$ {netTotal.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Pagamento</span>
                  <span style={{ fontWeight: 600, color: paymentTotal >= parseFloat(netTotal.toFixed(2)) ? '#2e7d32' : '#c62828' }}>
                    R$ {paymentTotal.toFixed(2)}
                  </span>
                </div>
                {changeAmount > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px dashed #e0e0e0', color: '#2e7d32' }}>
                    <span style={{ fontWeight: 500 }}>Troco</span>
                    <span style={{ fontWeight: 600, fontSize: '1.125rem' }}>R$ {changeAmount.toFixed(2)}</span>
                  </div>
                )}
              </div>

              <Button variant="primary" fullWidth size="lg" onClick={handleSubmit}
                disabled={processing || items.length === 0 || payments.length === 0 || paymentTotal < parseFloat(netTotal.toFixed(2))}
                style={{ marginTop: '24px', fontSize: '1rem', padding: '16px' }}>
                {processing ? 'Processando...' : 'Confirmar Venda'}
              </Button>
            </Card>
          </div>
        </div>
      </main>

      {/* Receipt Modal */}
      {receipt && (
        <Modal isOpen={!!receipt} onClose={() => setReceipt(null)} title="Venda Realizada">
          <div style={{ maxWidth: '400px' }}>
            <div style={{ textAlign: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid #e0e0e0' }}>
              <h3 style={{ margin: '0 0 8px', fontSize: '1.25rem', fontWeight: 600 }}>Zyrp PDV</h3>
              <p style={{ margin: 0, color: '#757575', fontSize: '0.875rem' }}>Cupom Não Fiscal</p>
            </div>
            <div style={{ fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span>Venda</span><strong>#{String(receipt.id).slice(0, 8)}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span>Data</span><span>{new Date(receipt.created_at).toLocaleString('pt-BR')}</span>
              </div>
              <div style={{ borderTop: '1px solid #e0e0e0', borderBottom: '1px solid #e0e0e0', padding: '16px 0', margin: '16px 0' }}>
                {receipt.items?.map((item: any) => (
                  <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', gap: '16px', marginBottom: '8px', fontSize: '0.875rem' }}>
                    <span>
                      <span>{item.product?.name || 'Produto'}</span>
                      <span style={{ marginLeft: '6px', color: '#757575' }}>
                        x{formatReceiptQuantity(item.quantity)}
                      </span>
                    </span>
                    <span>R$ {Number(item.line_total).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Total</span>
                <span style={{ fontWeight: 600, color: '#1976d2' }}>R$ {Number(receipt.net_total).toFixed(2)}</span>
              </div>
              <div style={{ textAlign: 'center', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #e0e0e0', color: '#757575', fontSize: '0.75rem' }}>
                Obrigado pela preferência!
              </div>
              <Button variant="primary" fullWidth onClick={handlePrintReceipt} style={{ marginTop: '24px' }}>
                Imprimir Cupom
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
