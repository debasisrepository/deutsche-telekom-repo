import { describe, it, expect, vi } from 'vitest';

// Mock useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ longlistId: 'LL-2024-0402' }),
  };
});

describe('LockAndDispatchPage', () => {
  it('can import the page component', async () => {
    const module = await import('../pages/LockAndDispatchPage');
    expect(module.default).toBeDefined();
  });

  it('imports dispatch components correctly', async () => {
    const { LockDetail } = await import('../components/dispatch/LockDetail');
    const { DispatchTable } = await import('../components/dispatch/DispatchTable');
    const { DispatchStatusBadge } = await import('../components/dispatch/DispatchStatusBadge');
    expect(LockDetail).toBeDefined();
    expect(DispatchTable).toBeDefined();
    expect(DispatchStatusBadge).toBeDefined();
  });
});
