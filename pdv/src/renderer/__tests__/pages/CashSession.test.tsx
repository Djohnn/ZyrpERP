import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { CashSession } from '../../pages/CashSession';

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
}));

vi.mock('../../contexts/CashSessionContext', () => ({
  useCashSession: () => ({
    session: {
      sessionId: 'cash-1',
      status: 'open',
      openingAmount: '100.00',
      expectedAmount: '149.90',
      salesCount: 1,
      totalSales: '49.90',
    },
    openSession: vi.fn(),
    closeSession: vi.fn(),
    refreshSession: vi.fn(),
  }),
}));

describe('CashSession', () => {
  it('renders open cash session summary without crashing', () => {
    render(
      <MemoryRouter>
        <CashSession />
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: 'Gestão de Caixa' })).toBeInTheDocument();
    expect(screen.getByText('Aberto')).toBeInTheDocument();
    expect(screen.getByText('49.90')).toBeInTheDocument();
  });
});
