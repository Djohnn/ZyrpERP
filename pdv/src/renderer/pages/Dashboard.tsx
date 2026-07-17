import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCashSession } from '../contexts/CashSessionContext';
import { Card, Button, CardHeader, CardContent, EmptyState, Spinner } from '../components/ui';

export function Dashboard() {
  const { isAuthenticated, deviceId, branchId } = useAuth();
  const { session, refreshSession } = useCashSession();
  const [loading, setLoading] = useState(true);
  const [recentSales, setRecentSales] = useState<any[]>([]);

  useEffect(() => {
    const init = async () => {
      await refreshSession();
      setLoading(false);
    };
    init();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '4px' }}>Dashboard</h1>
          <p style={{ color: '#757575', fontSize: '0.875rem' }}>
            {session.sessionId ? `Caixa ${session.status === 'open' ? 'aberto' : 'fechado'}` : 'Nenhum caixa aberto'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          {session.sessionId ? (
            <Link to="/cash-session"><Button variant="outline">Gerenciar Caixa</Button></Link>
          ) : (
            <Link to="/cash-session"><Button variant="outline">Abrir Caixa</Button></Link>
          )}
          <Link to="/sale"><Button>Nova Venda</Button></Link>
        </div>
      </div>

      {session.sessionId ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <Card><CardContent>
            <div style={{ fontSize: '0.875rem', color: '#757575', marginBottom: '4px' }}>Abertura</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.openingAmount}</div>
            <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Valor de abertura</div>
          </CardContent></Card>
          <Card><CardContent>
            <div style={{ fontSize: '0.875rem', color: '#757575', marginBottom: '4px' }}>Esperado</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.expectedAmount}</div>
            <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Valor esperado no caixa</div>
          </CardContent></Card>
          <Card><CardContent>
            <div style={{ fontSize: '0.875rem', color: '#757575', marginBottom: '4px' }}>Vendas</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.salesCount || 0}</div>
            <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Vendas realizadas</div>
          </CardContent></Card>
          <Card><CardContent>
            <div style={{ fontSize: '0.875rem', color: '#757575', marginBottom: '4px' }}>Total Vendido</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{session.totalSales}</div>
            <div style={{ fontSize: '0.75rem', color: '#757575', marginTop: '4px' }}>Total em vendas</div>
          </CardContent></Card>
        </div>
      ) : (
        <Card style={{ padding: '48px 24px', textAlign: 'center' }}>
          <EmptyState
            icon={<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="2" width="16" height="20" rx="2"/><path d="M4 10h16"/><path d="M8 14h8"/><path d="M12 18h4"/>
            </svg>}
            title="Nenhum caixa aberto"
            description="Abra o caixa para começar a vender"
            action={{ label: 'Abrir Caixa', onClick: () => window.location.href = '/cash-session' }}
          />
        </Card>
      )}

      <section style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Vendas Recentes</h2>
        </div>

        {recentSales.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600, fontSize: '0.75rem', color: '#757575', textTransform: 'uppercase' }}>Venda</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, fontSize: '0.75rem', color: '#757575', textTransform: 'uppercase' }}>Cliente</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: 600, fontSize: '0.75rem', color: '#757575', textTransform: 'uppercase' }}>Total</th>
                  <th style={{ padding: '12px 16px', textAlign: 'center', fontWeight: 600, fontSize: '0.75rem', color: '#757575', textTransform: 'uppercase' }}>Status</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, fontSize: '0.75rem', color: '#757575', textTransform: 'uppercase' }}>Hora</th>
                </tr>
              </thead>
              <tbody>
                {recentSales.slice(0, 5).map((sale: any) => (
                  <tr key={sale.id} style={{ borderBottom: '1px solid #f5f5f5' }}>
                    <td style={{ padding: '12px 16px', fontSize: '0.875rem' }}>#{sale.id.slice(0, 8)}</td>
                    <td style={{ padding: '12px 16px', fontSize: '0.875rem' }}>{sale.customer || 'Consumidor final'}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600 }}>{sale.net_total}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                      <span style={{
                        padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 500,
                        backgroundColor: sale.status === 'confirmed' ? '#e8f5e9' : sale.status === 'cancelled' ? '#fce4ec' : '#fff3e0',
                        color: sale.status === 'confirmed' ? '#2e7d32' : sale.status === 'cancelled' ? '#c62828' : '#f57c00'
                      }}>
                        {sale.status === 'confirmed' ? 'Confirmada' : sale.status === 'cancelled' ? 'Cancelada' : 'Pendente'}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '0.875rem', color: '#757575' }}>
                      {new Date(sale.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Card style={{ padding: '48px 24px', textAlign: 'center' }}>
            <EmptyState
              icon={<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7h16v10l-8 4m0-10L4 7m0 10l8 4"/>
              </svg>}
              title="Nenhuma venda registrada"
              description="Faça sua primeira venda do dia"
            />
          </Card>
        )}
      </section>
    </div>
  );
}
