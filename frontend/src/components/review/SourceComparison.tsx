import { TextInput, Stack } from '@carbon/react';
import './SourceComparison.scss';

interface SourceComparisonProps {
  rawExcerpt: string;
  fieldName?: string;
  fieldValue?: string;
  onFieldChange?: (value: string) => void;
}

export function SourceComparison({
  rawExcerpt,
  fieldName,
  fieldValue,
  onFieldChange,
}: SourceComparisonProps) {
  return (
    <Stack gap={5}>
      <h2 className="cds--productive-heading-03">Source comparison</h2>
      <div className="source-comparison-card">
        <span className="cds--label">Raw artifact excerpt (PII masked)</span>
        <div className="source-comparison-excerpt cds--type-mono">
          {rawExcerpt}
        </div>
        <p className="cds--helper-text-01 source-comparison-help">
          Highlighted evidence: budget statement is non-numeric; delivery locations mentioned.
        </p>
      </div>
      {fieldName && (
        <TextInput
          id={`correct-${fieldName}`}
          labelText={`Correct ${fieldName}`}
          value={fieldValue || ''}
          onChange={(e) => onFieldChange?.(e.target.value)}
          invalid={fieldName === 'budget_indication'}
          invalidText={
            fieldName === 'budget_indication'
              ? 'Numeric range was inferred, not stated. Replace with the source wording.'
              : undefined
          }
        />
      )}
    </Stack>
  );
}
