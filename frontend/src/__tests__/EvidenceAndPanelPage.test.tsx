import { describe, it, expect, vi } from 'vitest';
import { apiClient } from '../lib/api-client';

vi.mock('../lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

describe('EvidenceAndPanelPage', () => {
  it('can import the page component', async () => {
    const { EvidenceAndPanelPage } = await import('../pages/EvidenceAndPanelPage');
    expect(EvidenceAndPanelPage).toBeDefined();
  });

  it('API client post method is available', () => {
    expect(apiClient.post).toBeDefined();
  });
});
