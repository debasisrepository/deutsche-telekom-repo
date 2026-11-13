import { Tag } from '@carbon/react';
import './ClassificationCard.scss';

interface ClassificationCardProps {
  verdict: 'single_resource' | 'it_service';
  confidence: number;
  rationale?: string;
  reviewThreshold?: number;
}

export function ClassificationCard({
  verdict,
  confidence,
  rationale,
  reviewThreshold = 0.80,
}: ClassificationCardProps) {
  const verdictLabel = verdict === 'single_resource' ? 'single_resource' : 'it_service';
  const verdictTag = verdict === 'single_resource' ? 'red' : 'blue';
  const verdictType = verdict === 'single_resource' 
    ? 'Individual role or staff augmentation' 
    : 'Outcome / deliverable based';

  const thresholdPercent = Math.round(reviewThreshold * 100);

  return (
    <div className="classification-card">
      <span className="classification-card__label">classification_verdict</span>
      <div className="classification-card__verdict">
        <span className="classification-card__verdict-text">{verdictLabel}</span>
        <Tag type={verdictTag}>{verdictType}</Tag>
      </div>

      <span className="classification-card__label classification-card__confidence-label">
        classification_confidence
      </span>
      <div className="classification-card__confidence-value">{confidence.toFixed(2)}</div>
      
      <div className="classification-card__meter" role="img" aria-label={`Confidence ${confidence.toFixed(2)} against review threshold ${reviewThreshold.toFixed(2)}`}>
        <div className="classification-card__meter-fill" />
        <div 
          className="classification-card__meter-threshold" 
          data-position={thresholdPercent}
        />
      </div>
      <div className="classification-card__help">
        Review threshold {reviewThreshold.toFixed(2)}. Zone left of the marker is held for review; this case is {confidence >= reviewThreshold ? 'above' : 'below'} the threshold.
      </div>

      {rationale && (
        <>
          <h3 className="classification-card__heading">Rationale (rubric match)</h3>
          <div className="classification-card__rationale">{rationale}</div>
        </>
      )}
    </div>
  );
}
