import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

interface CashSessionState {
  sessionId: string | null;
  status: 'closed' | 'open';
  openingAmount: string;
  expectedAmount: string;
  salesCount: number;
  totalSales: string;
}

interface CashSessionContextType {
  session: CashSessionState;
  setSession: (session: Partial<CashSessionState>) => void;
  clearSession: () => void;
  openSession: (branchId: string, openingAmount: string) => Promise<{ success: boolean; error?: string }>;
  closeSession: (closingAmount: string) => Promise<{ success: boolean; error?: string }>;
  getCurrentSession: (branchId: string) => Promise<void>;
  refreshSession: () => Promise<void>;
}

const CashSessionContext = createContext<CashSessionContextType | null>(null);

const API_BASE = '/api/v1';

function defaultSession(): CashSessionState {
  return {
    sessionId: null,
    status: 'closed',
    openingAmount: '0.00',
    expectedAmount: '0.00',
    salesCount: 0,
    totalSales: '0.00',
  };
}

function loadSession(): CashSessionState {
  try {
    const saved = localStorage.getItem('cash_session');
    return saved ? { ...defaultSession(), ...JSON.parse(saved) } : defaultSession();
  } catch {
    return defaultSession();
  }
}

function saveSession(session: CashSessionState) {
  localStorage.setItem('cash_session', JSON.stringify(session));
}

export function CashSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<CashSessionState>(loadSession);

  useEffect(() => {
    const saved = loadSession();
    setSessionState(saved);
  }, []);

  const setSession = useCallback((newSession: Partial<CashSessionState>) => {
    setSessionState(prev => {
      const updated = { ...prev, ...newSession };
      localStorage.setItem('cash_session', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem('cash_session');
    setSessionState(defaultSession());
  }, []);

  const openSession = async (branchId: string, openingAmount: string) => {
    try {
      const response = await fetch(`${API_BASE}/cash-sessions/open/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ branch: branchId, opening_amount: openingAmount }),
      });

      if (!response.ok) {
        const error = await response.json();
        return { success: false, error: error.detail || 'Failed to open cash session' };
      }

      const data = await response.json();
      const updated = {
        sessionId: data.id,
        status: 'open' as const,
        openingAmount: data.opening_amount,
        expectedAmount: data.expected_amount,
        salesCount: 0,
        totalSales: '0.00',
      };
      setSessionState(updated);
      saveSession(updated as CashSessionState);

      return { success: true };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Failed to open cash session' };
    }
  };

  const closeSession = async (closingAmount: string) => {
    if (!session.sessionId) {
      return { success: false, error: 'No open cash session' };
    }

    try {
      const response = await fetch(`${API_BASE}/cash-sessions/${session.sessionId}/close/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ closing_amount: closingAmount }),
      });

      if (!response.ok) {
        const error = await response.json();
        return { success: false, error: error.detail || 'Failed to close cash session' };
      }

      clearSession();
      return { success: true };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Failed to close cash session' };
    }
  };

  const getCurrentSession = async (branchId: string) => {
    try {
      const response = await fetch(`${API_BASE}/cash-sessions/current/?branch=${branchId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      });

      if (response.ok) {
        const data = await response.json();
        const updated = {
          sessionId: data.id,
          status: data.status,
          openingAmount: data.opening_amount,
          expectedAmount: data.expected_amount,
          salesCount: data.sales_count ?? 0,
          totalSales: data.total_sales ?? '0.00',
        };
        setSessionState(updated);
        saveSession(updated as CashSessionState);
      } else if (response.status === 404) {
        clearSession();
      }
    } catch (error) {
      console.error('Failed to get current session:', error);
    }
  };

  const refreshSession = async () => {
    const branchId = localStorage.getItem('branch_id');
    if (branchId) {
      await getCurrentSession(branchId);
    }
  };

  return (
    <CashSessionContext.Provider value={{
      session,
      setSession,
      clearSession,
      openSession,
      closeSession,
      getCurrentSession,
      refreshSession,
    }}>
      {children}
    </CashSessionContext.Provider>
  );
}

export function useCashSession() {
  const context = useContext(CashSessionContext);
  if (!context) {
    throw new Error('useCashSession must be used within a CashSessionProvider');
  }
  return context;
}
