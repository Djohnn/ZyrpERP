import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SaleConfirmationToast } from '../../components/SaleConfirmationToast';

describe('SaleConfirmationToast', () => {
  const defaultProps = {
    saleId: 'abc-123',
    saleNumber: 'ABC12345',
    hasFiscalConfig: true,
    onPrintFiscal: vi.fn(),
    onPrintBalcao: vi.fn(),
    onClose: vi.fn(),
  };

  it('renders sale number', () => {
    render(<SaleConfirmationToast {...defaultProps} />);
    expect(screen.getByText(/ABC12345/)).toBeDefined();
  });

  it('renders success message', () => {
    render(<SaleConfirmationToast {...defaultProps} />);
    expect(screen.getByText(/realizada com sucesso/)).toBeDefined();
  });

  it('renders fiscal print button enabled when hasFiscalConfig is true', () => {
    render(<SaleConfirmationToast {...defaultProps} />);
    const btn = screen.getByText('Imprimir Cupom Fiscal');
    expect(btn).toBeDefined();
    expect((btn as HTMLButtonElement).disabled).toBe(false);
  });

  it('renders fiscal print button disabled when hasFiscalConfig is false', () => {
    render(<SaleConfirmationToast {...defaultProps} hasFiscalConfig={false} />);
    const btn = screen.getByText('Imprimir Cupom Fiscal');
    expect((btn as HTMLButtonElement).disabled).toBe(true);
  });

  it('renders balcao print button', () => {
    render(<SaleConfirmationToast {...defaultProps} />);
    expect(screen.getByText('Imprimir Cupom Balcão')).toBeDefined();
  });

  it('renders close button', () => {
    render(<SaleConfirmationToast {...defaultProps} />);
    expect(screen.getByText('Fechar')).toBeDefined();
  });

  it('calls onPrintFiscal when fiscal button clicked', () => {
    const onPrintFiscal = vi.fn();
    render(<SaleConfirmationToast {...defaultProps} onPrintFiscal={onPrintFiscal} />);
    fireEvent.click(screen.getByText('Imprimir Cupom Fiscal'));
    expect(onPrintFiscal).toHaveBeenCalledOnce();
  });

  it('calls onPrintBalcao when balcao button clicked', () => {
    const onPrintBalcao = vi.fn();
    render(<SaleConfirmationToast {...defaultProps} onPrintBalcao={onPrintBalcao} />);
    fireEvent.click(screen.getByText('Imprimir Cupom Balcão'));
    expect(onPrintBalcao).toHaveBeenCalledOnce();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn();
    render(<SaleConfirmationToast {...defaultProps} onClose={onClose} />);
    fireEvent.click(screen.getByText('Fechar'));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
