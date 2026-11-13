import { Button, Tag, InlineNotification } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import './CoverageGapCard.scss';

interface CoverageGapCardProps {
  coverageGapFlag: boolean;
  capabilityGap?: string;
  onStartNicheResearch: () => void;
}

export function CoverageGapCard({
  coverageGapFlag,
  capabilityGap,
  onStartNicheResearch,
}: CoverageGapCardProps) {
  if (!coverageGapFlag) {
    return null;
  }

  return (
    <div className="coverage-gap-card">
      <span className="cds--label">coverage_gap_flag</span>
      <div className="coverage-gap-header">
        <Tag type="warm-gray">true</Tag>
        <span className="coverage-gap-title">Capability gap detected</span>
      </div>
      <p className="coverage-gap-description">
        Panels cover cloud migration but not{' '}
        <strong>{capabilityGap || 'sovereign-cloud data classification for OT workloads'}</strong>. 
        No supplier is recommended implicitly for this gap.
      </p>
      <div className="coverage-gap-actions">
        <Button
          onClick={onStartNicheResearch}
          renderIcon={ArrowRight}
          iconDescription="Start niche research"
        >
          Start niche research (ATS7)
        </Button>
      </div>
      <p className="cds--helper-text-01">
        Coverage-gap signalling is the only trigger for ATS7.
      </p>
      <InlineNotification
        kind="error"
        title="Failure state example."
        subtitle="If the catalog returns no coverage for a category, the failure is shown here and no candidate suppliers are produced."
        lowContrast
        hideCloseButton
      />
    </div>
  );
}
