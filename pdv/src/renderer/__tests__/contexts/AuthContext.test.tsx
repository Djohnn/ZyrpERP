import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';

const API_BASE = '/api/v1';

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

function TestComponent() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="auth-status">{auth.isAuthenticated ? 'autenticado' : 'nao-autenticado'}</span>
      <span data-testid="device-id">{auth.deviceId || 'none'}</span>
      <span data-testid="branch-id">{auth.branchId || 'none'}</span>
      <button data-testid="btn-login" onClick={() => auth.login('test-key-123')}>Login</button>
      <button data-testid="btn-logout" onClick={() => auth.logout()}>Logout</button>
    </div>
  );
}

function renderWithProviders() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('AuthContext', () => {
  it('starts unauthenticated when no token', () => {
    renderWithProviders();
    expect(screen.getByTestId('auth-status')).toHaveTextContent('nao-autenticado');
  });

  it('restores authenticated from localStorage', () => {
    localStorage.setItem('access_token', 'valid-token');
    localStorage.setItem('device_id', 'dev-1');
    localStorage.setItem('branch_id', 'branch-1');
    renderWithProviders();
    expect(screen.getByTestId('auth-status')).toHaveTextContent('autenticado');
    expect(screen.getByTestId('device-id')).toHaveTextContent('dev-1');
    expect(screen.getByTestId('branch-id')).toHaveTextContent('branch-1');
  });

  it('login succeeds and updates state', async () => {
    const mockFetch = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        token: 'new-token',
        refresh_token: 'new-refresh',
        device_id: 'dev-2',
        branch_id: 'branch-2',
      }), { status: 200 })
    );

    renderWithProviders();
    const user = userEvent.setup();
    await user.click(screen.getByTestId('btn-login'));

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('autenticado');
    });
    expect(screen.getByTestId('device-id')).toHaveTextContent('dev-2');
    expect(screen.getByTestId('branch-id')).toHaveTextContent('branch-2');
    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE}/devices/validate/`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ api_key: 'test-key-123' }),
      })
    );
  });

  it('login failure returns error without changing state', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid API key' }), { status: 401 })
    );

    renderWithProviders();
    const user = userEvent.setup();
    await user.click(screen.getByTestId('btn-login'));

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('nao-autenticado');
    });
  });

  it('logout clears state', async () => {
    localStorage.setItem('access_token', 'valid-token');
    localStorage.setItem('refresh_token', 'refresh');
    localStorage.setItem('device_id', 'dev-1');
    localStorage.setItem('branch_id', 'branch-1');

    renderWithProviders();
    expect(screen.getByTestId('auth-status')).toHaveTextContent('autenticado');

    const user = userEvent.setup();
    await user.click(screen.getByTestId('btn-logout'));

    expect(screen.getByTestId('auth-status')).toHaveTextContent('nao-autenticado');
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});
