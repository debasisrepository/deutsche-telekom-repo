import { describe, it, expect } from 'vitest';
import { ClassificationReviewPage } from '../pages/ClassificationReviewPage';

describe('ClassificationReviewPage', () => {
  it('exports ClassificationReviewPage component', () => {
    expect(ClassificationReviewPage).toBeDefined();
    expect(typeof ClassificationReviewPage).toBe('function');
  });
});
