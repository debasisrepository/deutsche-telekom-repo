import { WarningAltFilled } from '@carbon/icons-react';
import './ConfidenceBar.scss';

interface ConfidenceBarProps {
  value: number;
}

export function ConfidenceBar({ value }: ConfidenceBarProps) {
  const percentage = Math.round(value * 100);
  const isWarning = value < 0.75;

  return (
    <div className="confidence-bar-container">
      <div
        className="confidence-bar-track"
        role="img"
        aria-label={`${value.toFixed(2)}`}
      >
        <div
          className={`confidence-bar-fill ${value >= 0.75 ? 'confidence-bar-fill-green' : 'confidence-bar-fill-yellow'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {isWarning && (
        <WarningAltFilled size={16} className="confidence-bar-icon" aria-hidden="true" />
      )}
      <span>{value.toFixed(2)}</span>
    </div>
  );
}
