import { describe, it, expect, vi } from 'vitest';
import { apiClient } from '../lib/api-client';

vi.mock('../lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('AttributeReviewPage', () => {
  it('can import the page component', async () => {
    const { AttributeReviewPage } = await import('../pages/AttributeReviewPage');
    expect(AttributeReviewPage).toBeDefined();
  });

  it('API client is available', () => {
    expect(apiClient.get).toBeDefined();
    expect(apiClient.post).toBeDefined();
  });
});
