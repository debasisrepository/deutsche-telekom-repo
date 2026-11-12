import { Tag, ProgressBar } from '@carbon/react'
import { ClassificationReviewPayload } from '../../types/review'
import styles from './ClassificationReviewCard.module.css'

interface ClassificationReviewCardProps {
  classification: ClassificationReviewPayload
}

function getVerdictTag(verdict: 'it_service' | 'single_resource') {
  if (verdict === 'it_service') {
    return <Tag type="blue">IT service</Tag>
  }
  return <Tag type="cyan">Single resource</Tag>
}

export function ClassificationReviewCard({
  classification,
}: ClassificationReviewCardProps) {
  const confidencePercent = Math.round(classification.confidence_score * 100)

  return (
    <div className={styles.card}>
      <div className={styles.verdictRow}>
        {getVerdictTag(classification.ai_verdict)}
        <Tag type="purple">AI-generated</Tag>
      </div>

      <div className={styles.confidenceSection}>
        <p className={styles.label}>Confidence</p>
        <ProgressBar
          label="Classification confidence"
          hideLabel
          value={confidencePercent}
          max={100}
        />
        <p className={styles.confidenceValue}>
          <strong>{classification.confidence_score.toFixed(2)}</strong> · above the
          review-attention threshold
        </p>
      </div>

      <h3 className={styles.sectionHeading}>Rationale inputs</h3>
      <table className={styles.rationaleTable}>
        <thead>
          <tr>
            <th>Input attribute</th>
            <th>Value</th>
            <th>Points to</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(classification.rationale_inputs).map(([key, value]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{String(value)}</td>
              <td>
                <Tag type="gray">Neutral</Tag>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {classification.reasoning && (
        <div className={styles.reasoning}>
          <p className={styles.label}>Reasoning</p>
          <p>{classification.reasoning}</p>
        </div>
      )}
    </div>
  )
}
