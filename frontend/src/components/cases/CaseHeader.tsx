import { Tag } from '@carbon/react'
import { formatDateTime } from '../../lib/utils'
import styles from './CaseHeader.module.css'

interface CaseHeaderProps {
  caseNumber: string
  channel: string
  receivedAt: string
  needTitle: string
  sourceArtifact?: string
  workflowState: string
  nextAction: string
}

export function CaseHeader({
  caseNumber,
  channel,
  receivedAt,
  needTitle,
  sourceArtifact,
  workflowState,
  nextAction,
}: CaseHeaderProps) {
  return (
    <>
      <h2 className={`${styles.heading} cds--productive-heading-05`}>
        {caseNumber} · {needTitle}
      </h2>

      <dl className={styles.banner}>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Case ID</dt>
          <dd className={styles.bannerValueMono}>
            {caseNumber}
          </dd>
        </div>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Channel</dt>
          <dd className={styles.bannerValueMono}>
            {channel}
          </dd>
        </div>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Received (UTC)</dt>
          <dd className={styles.bannerValue}>{formatDateTime(receivedAt)}</dd>
        </div>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Source artifact</dt>
          <dd className={styles.bannerValue}>
            {sourceArtifact || 'N/A'}
          </dd>
        </div>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Current state</dt>
          <dd className={styles.bannerValue}>
            <Tag type="blue">{workflowState.replace(/_/g, ' ')}</Tag>
          </dd>
        </div>
        <div>
          <dt className={`${styles.bannerLabel} cds--label-01`}>Next required action</dt>
          <dd className={styles.bannerValue}>{nextAction}</dd>
        </div>
      </dl>
    </>
  )
}
