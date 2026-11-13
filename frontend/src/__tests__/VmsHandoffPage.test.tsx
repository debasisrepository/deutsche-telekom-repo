import { describe, it, expect } from 'vitest';
import { VmsHandoffPage } from '../pages/VmsHandoffPage';

describe('VmsHandoffPage', () => {
  it('exports VmsHandoffPage component', () => {
    expect(VmsHandoffPage).toBeDefined();
    expect(typeof VmsHandoffPage).toBe('function');
  });
});
