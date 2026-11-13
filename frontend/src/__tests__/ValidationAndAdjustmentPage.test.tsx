import { describe, it, expect, vi } from 'vitest';

// Mock useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ longlistId: 'LL-2024-0418' }),
  };
});

describe('ValidationAndAdjustmentPage', () => {
  it('can import the page component', async () => {
    const module = await import('../pages/ValidationAndAdjustmentPage');
    expect(module.default).toBeDefined();
  });

  it('imports components correctly', async () => {
    const { CountVisualization } = await import('../components/governance/CountVisualization');
    const { ValidationHistory } = await import('../components/governance/ValidationHistory');
    const { AdjustmentForm } = await import('../components/governance/AdjustmentForm');
    expect(CountVisualization).toBeDefined();
    expect(ValidationHistory).toBeDefined();
    expect(AdjustmentForm).toBeDefined();
  });
});
