import { describe, it, expect, vi } from 'vitest';
import { apiClient } from '../lib/api-client';

vi.mock('../lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('NeedIntakePage', () => {
  it('can import the page component', async () => {
    const { NeedIntakePage } = await import('../pages/NeedIntakePage');
    expect(NeedIntakePage).toBeDefined();
  });

  it('API client is available', () => {
    expect(apiClient.get).toBeDefined();
  });
});
