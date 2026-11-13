import { Tag, InlineNotification } from '@carbon/react';
import styles from './CountVisualization.module.scss';

interface CountVisualizationProps {
  currentCount: number;
  validationVerdict: 'pass' | 'fail';
}

export function CountVisualization({ currentCount, validationVerdict }: CountVisualizationProps) {
  const renderCountBand = () => {
    const positions = [0, 1, 2, 3, 4, 5, 6, 7, 8];
    return (
      <div className={styles.band} role="img" aria-label="Count scale 0 to 8: 0 to 2 fail, 3 to 6 pass, 7 to 8 fail. Current count.">
        {positions.map((pos) => {
          const isPass = pos >= 3 && pos <= 6;
          const isCurrent = pos === currentCount;
          return (
            <span
              key={pos}
              className={`${isPass ? styles.ok : ''} ${isCurrent ? styles.cur : ''}`}
            >
              {pos}
            </span>
          );
        })}
      </div>
    );
  };

  return (
    <div className={styles.card}>
      <span className={styles.label}>Current supplier set</span>
      <div className={styles.countDisplay}>
        <span className={styles.big}>{currentCount}</span>
        <Tag type={validationVerdict === 'pass' ? 'green' : 'red'}>
          validation_verdict: {validationVerdict}
        </Tag>
      </div>
      {renderCountBand()}
      <div className={styles.help}>
        Fewer than 3 fails (mandatory minimum). 3 to 6 passes. More than 6 fails.
      </div>
      {validationVerdict === 'fail' && (
        <InlineNotification
          kind="error"
          title="Violation: below mandatory minimum of 3."
          subtitle="Lock and dispatch are blocked. This is a hard stop, not a warning."
          hideCloseButton
          className={styles.notification}
        />
      )}
    </div>
  );
}
