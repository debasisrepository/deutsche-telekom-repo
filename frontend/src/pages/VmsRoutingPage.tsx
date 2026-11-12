import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Tag } from '@carbon/react'
import { Checkmark, Close } from '@carbon/icons-react'
import { apiClient } from '../lib/api-client'
import { formatDateTime } from '../lib/utils'
import styles from './VmsRoutingPage.module.css'

interface VMSHandoff {
  id: number
  case_id: number
  vms_reference_id: string
  handoff_status: string
  request_snapshot: Record<string, unknown>
  handed_off_at: string
}

interface CaseDetail {
  id: number
  case_number: string
  inbound_channel: string
  workflow_state: string
  next_action: string
  created_at: string
  updated_at: string
  source_artifacts: Array<{ storage_ref: string }>
  normalized_need?: {
    mandatory_fields: Record<string, unknown>
  }
  vms_handoff?: VMSHandoff
}

interface AuditEvent {
  action_type: string
  created_at: string
  actor_id: string
  audit_payload: Record<string, unknown>
}

export function VmsRoutingPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null)
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!caseId) return

      setIsLoading(true)
      setError(null)
      try {
        const caseResponse = await apiClient.get<CaseDetail>(`/cases/${caseId}`)
        setCaseDetail(caseResponse)

        // Simulate audit events for demonstration
        setAuditEvents([
          {
            action_type: 'Case created',
            created_at: caseResponse.created_at,
            actor_id: 'system (AGN5)',
            audit_payload: {},
          },
          {
            action_type: 'Extraction approved',
            created_at: caseResponse.created_at,
            actor_id: 'S. Brandt',
            audit_payload: {},
          },
          {
            action_type: 'Classification overridden',
            created_at: caseResponse.created_at,
            actor_id: 'S. Brandt',
            audit_payload: { rationale: 'One named individual profile requested.' },
          },
          {
            action_type: 'VMS handoff registered',
            created_at: caseResponse.vms_handoff?.handed_off_at || caseResponse.created_at,
            actor_id: 'M. Keller',
            audit_payload: { vms_reference_id: caseResponse.vms_handoff?.vms_reference_id || '' },
          },
        ])
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load case'
        setError(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [caseId])

  if (isLoading) {
    return (
      <div className={styles.main}>
        <p className={styles.loadingMessage}>Loading VMS routing details...</p>
      </div>
    )
  }

  if (error || !caseDetail) {
    return (
      <div className={styles.main}>
        <p className={styles.errorMessage}>{error || 'Case not found'}</p>
        <Link to="/" className={styles.errorLink}>
          Back to cases
        </Link>
      </div>
    )
  }

  const mandatoryFields = caseDetail.normalized_need?.mandatory_fields || {}
  const sourceArtifactRef = caseDetail.source_artifacts[0]?.storage_ref || 'N/A'
  const vmsHandoff = caseDetail.vms_handoff

  const getWorkflowSteps = () => {
    return [
      { label: 'Intake', description: 'Complete', status: 'done' },
      { label: 'Extraction', description: 'Approved', status: 'done' },
      { label: 'Classification', description: 'Single resource (overridden)', status: 'done' },
      { label: 'Evidence and mapping', description: 'Closed – routed out', status: 'closed' },
      { label: 'Longlist', description: 'Closed – routed out', status: 'closed' },
      { label: 'Lock', description: 'Closed – routed out', status: 'closed' },
      { label: 'Dispatch', description: 'Closed – routed out', status: 'closed' },
    ]
  }

  const steps = getWorkflowSteps()

  return (
    <div className={styles.main}>
        <p className={`${styles.breadcrumb} cds--body-compact-01`}>
          <Link to="/" className={styles.breadcrumbLink}>
            Cases
          </Link>{' '}
          / {caseDetail.case_number} / VMS routing
        </p>

        <h1 className={`${styles.pageHeading} cds--productive-heading-05`}>
          {caseDetail.case_number} · Routed to Vendor Management System
        </h1>

        <ol className={styles.stepper} aria-label="Case progress">
          {steps.map((step, index) => (
            <li
              key={index}
              className={`${styles.step} ${styles[step.status]}`}
              aria-current={step.status === 'current' ? 'step' : undefined}
            >
              {step.status === 'done' && (
                <Checkmark size={16} className={styles.icon} aria-hidden="true" />
              )}
              {step.status === 'closed' && (
                <span className={styles.ringClosed} aria-hidden="true" />
              )}
              <b className={`${styles.stepLabel} cds--label-02`}>{step.label}</b>
              <span className={`${styles.stepDescription} cds--label-01`}>{step.description}</span>
            </li>
          ))}
        </ol>

        <dl className={styles.banner}>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Case ID</dt>
            <dd className={styles.bannerValueMono}>{caseDetail.case_number}</dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Channel</dt>
            <dd className={styles.bannerValueMono}>{caseDetail.inbound_channel}</dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Received (UTC)</dt>
            <dd className={styles.bannerValue}>{formatDateTime(caseDetail.created_at)}</dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Source artifact</dt>
            <dd className={styles.bannerValue}>{sourceArtifactRef}</dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Current state</dt>
            <dd className={styles.bannerValue}>
              <Tag type="gray">Routed to VMS</Tag>
            </dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Next required action</dt>
            <dd className={styles.bannerValue}>None – selection path closed</dd>
          </div>
        </dl>

        <div className={styles.successNote} role="status">
          <Checkmark size={16} className={styles.successIcon} aria-hidden="true" />
          <div>
            <b>Handoff registered.</b> This case is a single-resource need and is no longer part of
            the IT-service supplier-selection workflow. It is shown as "Routed out · VMS" in the
            case list.
          </div>
        </div>

        <div className={styles.grid}>
          <section className={styles.column8} aria-labelledby="handoff-heading">
            <h2 id="handoff-heading" className={`${styles.sectionHeading} cds--productive-heading-03`}>
              VMS handoff record
            </h2>
            <dl className={styles.keyValueList}>
              <dt>VMS reference ID</dt>
              <dd className={styles.monoValue}>{vmsHandoff?.vms_reference_id || 'N/A'}</dd>

              <dt>Handoff status</dt>
              <dd>
                {vmsHandoff?.handoff_status === 'success' ? (
                  <Tag type="green">Registered</Tag>
                ) : (
                  <Tag type="red">Failed</Tag>
                )}
              </dd>

              <dt>Confirmed classification</dt>
              <dd>Single resource</dd>

              <dt>Original system verdict</dt>
              <dd>IT service (0.64) – overridden by reviewer</dd>

              <dt>Handed off</dt>
              <dd>
                {vmsHandoff?.handed_off_at ? formatDateTime(vmsHandoff.handed_off_at) : 'N/A'} · by
                M. Keller
              </dd>

              <dt>Request snapshot</dt>
              <dd>
                {String(mandatoryFields.service_category || 'N/A')} ·{' '}
                {String(mandatoryFields.estimated_duration || 'N/A')} ·{' '}
                {String(mandatoryFields.location || 'N/A')} · start{' '}
                {String(mandatoryFields.planned_start || 'N/A')}
              </dd>
            </dl>
          </section>

          <section className={styles.column8} aria-labelledby="audit-heading">
            <h2 id="audit-heading" className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Audit trail for this case
            </h2>
            <ul className={styles.auditList}>
              {auditEvents.map((event, index) => (
                <li key={index} className={styles.auditItem}>
                  <b>{event.action_type}</b>
                  <br />
                  <span className={`${styles.auditLabel} cds--label-01`}>
                    {formatDateTime(event.created_at)} · {event.actor_id}
                    {event.audit_payload.rationale ? ` · "${String(event.audit_payload.rationale)}"` : ''}
                    {event.audit_payload.vms_reference_id ? ` · ${String(event.audit_payload.vms_reference_id)}` : ''}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className={styles.column16} aria-labelledby="exception-heading">
            <h2
              id="exception-heading"
              className={`${styles.sectionHeading} cds--productive-heading-03`}
            >
              Handoff exception state
            </h2>
            <div className={styles.errorNote} role="alert">
              <Close size={16} className={styles.errorIcon} aria-hidden="true" />
              <div>
                <b>If the VMS handoff fails:</b> the case remains in "routed-pending-retry" with
                the failure reason shown here, and the supplier-selection path stays open until a
                handoff is registered. VMS handoff is allowed only when the confirmed
                classification is single resource; any other request is rejected with a state
                conflict.
              </div>
            </div>
          </section>
        </div>

        <p className={`${styles.footer} cds--label-01`}>
          Wireframe 05 of 08 · Covers FR-008, FR-010 · IBM Carbon White theme · Working tier
        </p>
      </div>
  )
}
