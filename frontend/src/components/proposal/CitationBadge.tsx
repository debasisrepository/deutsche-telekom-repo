import { Tag } from '@carbon/react';
import './CitationBadge.scss';

interface CitationBadgeProps {
  citationCoverage: number;
  required?: number;
}

export function CitationBadge({ citationCoverage, required = 98 }: CitationBadgeProps) {
  const isValid = citationCoverage >= required;

  return (
    <div className="citation-badge-container">
      <span className="cds--label">Citation coverage</span>
      <div className="citation-badge-display">
        <Tag type={isValid ? 'green' : 'red'} size="md">
          {citationCoverage}%
        </Tag>
        <span className="citation-badge-text">
          {isValid ? `(meets ${required}% requirement)` : `(below ${required}% requirement)`}
        </span>
      </div>
    </div>
  );
}
