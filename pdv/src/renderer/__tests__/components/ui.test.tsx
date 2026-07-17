import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button, Card, Input, Modal, Spinner, Toast, EmptyState } from '../../components/ui';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('shows spinner when loading', () => {
    const { container } = render(<Button loading>Save</Button>);
    expect(container.querySelector('span[style*="position: absolute"]')).toBeTruthy();
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('is disabled when loading', () => {
    render(<Button loading>Save</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is disabled when disabled prop', () => {
    render(<Button disabled>Save</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('applies fullWidth style', () => {
    render(<Button fullWidth>Full</Button>);
    expect(screen.getByRole('button')).toHaveStyle('width: 100%');
  });
});

describe('Card', () => {
  it('renders children', () => {
    render(<Card><p>Content</p></Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('applies className', () => {
    const { container } = render(<Card className="my-card">Content</Card>);
    expect(container.firstChild).toHaveClass('my-card');
  });
});

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Name" />);
    expect(screen.getByText('Name')).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<Input label="Name" error="Required" />);
    expect(screen.getByText('Required')).toBeInTheDocument();
  });

  it('forwards value and onChange', () => {
    const onChange = vi.fn();
    render(<Input value="test" onChange={onChange} />);
    const input = screen.getByRole('textbox') as HTMLInputElement;
    expect(input.value).toBe('test');
    fireEvent.change(input, { target: { value: 'new' } });
    expect(onChange).toHaveBeenCalled();
  });
});

describe('Modal', () => {
  it('renders nothing when closed', () => {
    const { container } = render(<Modal isOpen={false} onClose={() => {}}>Content</Modal>);
    expect(container.innerHTML).toBe('');
  });

  it('renders content when open', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Modal Title">Content</Modal>);
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Modal Title')).toBeInTheDocument();
  });

  it('calls onClose when clicking overlay', () => {
    const onClose = vi.fn();
    render(<Modal isOpen={true} onClose={onClose}>Content</Modal>);
    fireEvent.click(screen.getByText('Content').closest('[style*="position: fixed"]')!);
    expect(onClose).toHaveBeenCalled();
  });
});

describe('Spinner', () => {
  it('renders with default size', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
    expect(svg?.getAttribute('width')).toBe('24');
  });

  it('renders with large size', () => {
    const { container } = render(<Spinner size="lg" />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('width')).toBe('40');
  });
});

describe('Toast', () => {
  it('renders message', () => {
    render(<Toast message="Saved!" type="success" onClose={() => {}} />);
    expect(screen.getByText('Saved!')).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn();
    render(<Toast message="Error" type="error" onClose={onClose} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClose).toHaveBeenCalled();
  });
});

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState icon={<span>icon</span>} title="Empty" description="No data" />);
    expect(screen.getByText('Empty')).toBeInTheDocument();
    expect(screen.getByText('No data')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const onClick = vi.fn();
    render(<EmptyState icon={<span>icon</span>} title="Empty" description="No data"
      action={{ label: 'Add', onClick }} />);
    fireEvent.click(screen.getByText('Add'));
    expect(onClick).toHaveBeenCalled();
  });
});
