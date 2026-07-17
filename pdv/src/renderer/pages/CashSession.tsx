import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCashSession } from '../contexts/CashSessionContext';
import { Card, Button, InputGroup, Spinner } from '../components/ui';

export function CashSession() {
  const { isAuthenticated } = useAuth();
  const { session, openSession, closeSession, refreshSession } = useCashSession();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [openingAmount, setOpeningAmount] = useState('');
  const [closingAmount, setClosingAmount] = useState('');
  const [error, setError] = useState('');
  const [showCloseModal, setShowCloseModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    refreshSession();
    setLoading(false);
  }, [isAuthenticated, navigate]);

  const handleOpen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!openingAmount || parseFloat(openingAmount) <= 0) {
      setError('Informe um valor de abertura válido');
      return;
    }
    try {
      const result = await openSession(localStorage.getItem('branch_id') || '', openingAmount);
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Erro ao abrir caixa');
      }
    } catch {
      setError('Erro ao abrir caixa');
    }
  };

  const handleClose = async () => {
    if (!closingAmount || parseFloat(closingAmount) <= 0) {
      setError('Informe um valor de fechamento válido');
      return;
    }
    try {
      const result = await closeSession(closingAmount);
      if (result.success) {
        setShowCloseModal(false);
        setClosingAmount('');
      } else {
        setError(result.error || 'Erro ao fechar caixa');
      }
    } catch {
      setError('Erro ao fechar caixa');
    }
  };

  if (!isAuthenticated) return null;

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '4px' }}>Gestão de Caixa</h1>
          <p style={{ color: '#757575', fontSize: '0.875rem' }}>
            {session.sessionId ? `Caixa ${session.status === 'open' ? 'aberto' : 'fechado'}` : 'Nenhum caixa aberto'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/dashboard"><Button variant="secondary">Dashboard</Button></Link>
          <Link to="/sale"><Button>Nova Venda</Button></Link>
        </div>
      </div>

      {session.sessionId ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <Card>
              <CardHeader><h3 style={{ margin: 0, fontSize: '0.875rem', color: '#757575', fontWeight: 500 }}>Status</h3></CardHeader>
              <CardContent>
                <span style={{
                  display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px',
                  borderRadius: '20px', fontSize: '0.875rem', fontWeight: 600,
                  backgroundColor: session.status === 'open' ? '#e8f5e9' : '#fce4ec',
                  color: session.status === 'open' ? '#2e7d32' : '#c62828'
                }}>
                  {session.status === 'open' ? 'Aberto' : 'Fechado'}
                </span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><h3 style={{ margin: 0, fontSize: '0.875rem', color: '#757575', fontWeight: 500 }}>Abertura</h3></CardHeader>
              <CardContent>
                <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.openingAmount}</div>
                <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Valor de abertura</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><h3 style={{ margin: 0, fontSize: '0.875rem', color: '#757575', fontWeight: 500 }}>Esperado</h3></CardHeader>
              <CardContent>
                <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.expectedAmount}</div>
                <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Valor esperado no caixa</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><h3 style={{ margin: 0, fontSize: '0.875rem', color: '#757575', fontWeight: 500 }}>Vendas</h3></CardHeader>
              <CardContent>
                <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.salesCount || 0}</div>
                <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Vendas realizadas</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><h3 style={{ margin: 0, fontSize: '0.875rem', color: '#757575', fontWeight: 500 }}>Total Vendido</h3></CardHeader>
              <CardContent>
                <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.totalSales}</div>
                <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Total em vendas</div>
              </CardContent>
            </Card>
          </div>

          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
            <Button variant="secondary" onClick={() => setShowCloseModal(true)} style={{ flex: 1 }}>Fechar Caixa</Button>
            <Link to="/sale" style={{ flex: 1 }}><Button style={{ width: '100%' }}>Nova Venda</Button></Link>
            <Link to="/dashboard" style={{ flex: 1 }}><Button variant="secondary" style={{ width: '100%' }}>Dashboard</Button></Link>
          </div>
        </>
      ) : (
        <Card style={{ padding: '48px 24px', textAlign: 'center' }}>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '16px', opacity: 0.5 }}>
            <rect x="4" y="2" width="16" height="20" rx="2"/>
            <path d="M4 10h16"/><path d="M8 14h8"/><path d="M12 18h4"/>
          </svg>
          <h3 style={{ margin: '16px 0 8px', fontSize: '1.125rem', fontWeight: 600 }}>Nenhum caixa aberto</h3>
          <p style={{ color: '#757575', marginBottom: '24px' }}>Abra o caixa para começar a vender</p>
          <form onSubmit={handleOpen}>
            <InputGroup style={{ maxWidth: '300px', margin: '0 auto 16px' }}>
              <label htmlFor="openingAmount">Valor de Abertura</label>
              <input type="number" id="openingAmount" step="0.01" min="0.01"
                value={openingAmount} onChange={(e) => setOpeningAmount(e.target.value)} placeholder="0,00" />
            </InputGroup>
            <Button type="submit" fullWidth style={{ marginTop: '16px' }}>Abrir Caixa</Button>
            {error && <div style={{ color: '#c62828', marginTop: '12px', fontSize: '0.875rem' }}>{error}</div>}
          </form>
        </Card>
      )}

      {showCloseModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{ background: '#fff', borderRadius: '12px', padding: '24px', maxWidth: '400px', width: '100%' }}>
            <h3 style={{ marginBottom: '16px' }}>Fechar Caixa</h3>
            <InputGroup style={{ marginBottom: '16px' }}>
              <label htmlFor="closingAmount">Valor de Fechamento</label>
              <input type="number" id="closingAmount" step="0.01" min="0.01"
                value={closingAmount} onChange={(e) => setClosingAmount(e.target.value)} placeholder="0,00" />
            </InputGroup>
            <div style={{ display: 'flex', gap: '12px' }}>
              <Button variant="secondary" onClick={() => setShowCloseModal(false)} style={{ flex: 1 }}>Cancelar</Button>
              <Button variant="danger" onClick={handleClose} style={{ flex: 1 }}>Fechar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const cellStyle = {
  padding: '12px 16px',
  fontSize: '0.875rem',
  color: '#212121',
  borderBottom: '1px solid #f0f0f0'
};
