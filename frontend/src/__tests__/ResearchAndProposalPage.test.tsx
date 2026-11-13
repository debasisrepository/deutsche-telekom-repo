import { describe, it, expect, vi } from 'vitest';
import { apiClient } from '../lib/api-client';

vi.mock('../lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

describe('ResearchAndProposalPage', () => {
  it('can import the page component', async () => {
    const { ResearchAndProposalPage } = await import('../pages/ResearchAndProposalPage');
    expect(ResearchAndProposalPage).toBeDefined();
  });

  it('API client post method is available', () => {
    expect(apiClient.post).toBeDefined();
  });
});
