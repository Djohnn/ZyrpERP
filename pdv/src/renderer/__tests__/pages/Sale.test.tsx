import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sale } from '../../pages/Sale';

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
}));

vi.mock('../../contexts/CashSessionContext', () => ({
  useCashSession: () => ({
    session: {
      sessionId: 'cash-1',
      status: 'open',
      openingAmount: '100.00',
      expectedAmount: '100.00',
      salesCount: 0,
      totalSales: '0.00',
    },
  }),
}));

describe('Sale', () => {
  it('shows a visible cash management action from the sale screen', () => {
    render(
      <MemoryRouter>
        <Sale />
      </MemoryRouter>,
    );

    expect(screen.getByRole('button', { name: 'Fechar Caixa' })).toBeInTheDocument();
  });

  it('adds API product with string price as numeric cart total', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        results: [{
          id: 'product-1',
          sku: 'PDV-001',
          name: 'Produto PDV',
          base_unit: 'unit-1',
          price: '49.90',
        }],
      }), { status: 200 }),
    );

    render(
      <MemoryRouter>
        <Sale />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByPlaceholderText('Buscar produto (SKU ou nome)...'), {
      target: { value: 'Produto PDV' },
    });

    fireEvent.click(await screen.findByText('Produto PDV'));

    await waitFor(() => {
      expect(screen.getByText('Carrinho (1)')).toBeInTheDocument();
      expect(screen.getAllByText('R$ 49.90').length).toBeGreaterThan(0);
    });
  });
});
