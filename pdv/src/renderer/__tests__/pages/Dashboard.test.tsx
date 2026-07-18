import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Dashboard } from '../../pages/Dashboard';

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    deviceId: 'device-1',
    branchId: 'branch-1',
  }),
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
    refreshSession: vi.fn().mockResolvedValue(undefined),
  }),
}));

describe('Dashboard', () => {
  it('shows a direct close cash action when cash session is open', async () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('button', { name: 'Fechar Caixa' })).toBeInTheDocument();
  });
});
