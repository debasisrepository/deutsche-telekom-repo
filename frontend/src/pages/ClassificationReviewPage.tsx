import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  InlineNotification,
  Button,
  TextArea,
  RadioButtonGroup,
  RadioButton,
  Stack,
  Tile,
} from '@carbon/react'
import { apiClient } from '../lib/api-client'
import { CaseDetail } from '../types/case'
import {
  ClassificationReviewPayload,
  ClassificationReviewDecisionRequest,
  ReviewDecisionResponse,
} from '../types/review'
import { CaseHeader } from '../components/cases/CaseHeader'
import { WorkflowStepper } from '../components/cases/WorkflowStepper'
import { ClassificationReviewCard } from '../components/reviews/ClassificationReviewCard'
import styles from './ClassificationReviewPage.module.css'

export function ClassificationReviewPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null)
  const [classification, setClassification] =
    useState<ClassificationReviewPayload | null>(null)
  const [decision, setDecision] = useState<'confirm' | 'override'>('confirm')
  const [overrideVerdict, setOverrideVerdict] = useState<'it_service' | 'single_resource'>(
    'it_service'
  )
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadCase() {
      if (!caseId) return
      try {
        const detail = await apiClient.get<CaseDetail>(`/cases/${caseId}`)
        setCaseDetail(detail)

        // Mock classification payload - in production, fetch from backend
        const mockClassification: ClassificationReviewPayload = {
          ai_verdict: 'it_service',
          confidence_score: 0.91,
          rationale_inputs: {
            'Delivery model': 'Team-based, managed outcome',
            'Service scope': 'Operate and develop platform',
            Duration: '24 months',
            'Individual named profile': 'None requested',
          },
          reasoning:
            'Classified as IT service based on team-based delivery model and managed outcome scope',
        }
        setClassification(mockClassification)
        setOverrideVerdict(mockClassification.ai_verdict)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load case')
      }
    }
    loadCase()
  }, [caseId])

  const handleConfirm = async () => {
    if (!caseId || !classification) return
    setLoading(true)
    setError(null)
    try {
      const request: ClassificationReviewDecisionRequest = {
        decision: 'confirm',
      }
      await apiClient.post<ReviewDecisionResponse>(
        `/cases/${caseId}/reviews/classification`,
        request
      )
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm classification')
    } finally {
      setLoading(false)
    }
  }

  const handleOverride = async () => {
    if (!caseId || !reason.trim()) {
      setError('Reason is required for override decision')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const request: ClassificationReviewDecisionRequest = {
        decision: 'override',
        confirmed_verdict: overrideVerdict,
      }
      await apiClient.post<ReviewDecisionResponse>(
        `/cases/${caseId}/reviews/classification`,
        request
      )
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to override classification')
    } finally {
      setLoading(false)
    }
  }

  if (!caseDetail || !classification) {
    return (
      <div className={styles.container}>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <nav className={styles.breadcrumb}>
        <Link to="/">Cases</Link> / <Link to={`/cases/${caseId}`}>{caseDetail.case_number}</Link> /
        Classification review
      </nav>

      <Stack gap={5}>
        <h1>Classification review and override</h1>

        <WorkflowStepper workflowState={caseDetail.workflow_state} />

        <CaseHeader
          caseNumber={caseDetail.case_number}
          channel={caseDetail.inbound_channel}
          receivedAt={caseDetail.created_at}
          needTitle={caseDetail.normalized_need?.mandatory_fields?.need_title || 'Untitled'}
          sourceArtifact={caseDetail.source_artifacts[0]?.storage_ref}
          workflowState={caseDetail.workflow_state}
          nextAction={caseDetail.next_action}
        />

        {error && (
          <InlineNotification
            kind="error"
            title="Error"
            subtitle={error}
            onCloseButtonClick={() => setError(null)}
          />
        )}

        <InlineNotification
          kind="warning"
          title="Human confirmation required (AMBER gate)."
          subtitle="The confirmed classification, not the system verdict, controls routing."
          hideCloseButton
        />

        <ClassificationReviewCard classification={classification} />

        <div className={styles.card}>
              <h2>Reviewer decision</h2>

              <fieldset className={styles.fieldset}>
                <legend className={styles.label}>Final classification</legend>
                <RadioButtonGroup
                  name="decision"
                  valueSelected={decision}
                  onChange={(value) => setDecision(value as 'confirm' | 'override')}
                >
                  <RadioButton
                    id="confirm"
                    value="confirm"
                    labelText={
                      <div>
                        <strong>Confirm IT service</strong>
                        <br />
                        <span className={styles.helperText}>
                          Continue to evidence retrieval and panel mapping.
                        </span>
                      </div>
                    }
                  />
                  <RadioButton
                    id="override"
                    value="override"
                    labelText={
                      <div>
                        <strong>Override to single resource</strong>
                        <br />
                        <span className={styles.helperText}>
                          Route to the Vendor Management System; supplier selection closes.
                        </span>
                      </div>
                    }
                  />
                </RadioButtonGroup>
              </fieldset>

              {decision === 'override' && (
                <div className={styles.formField}>
                  <RadioButtonGroup
                    name="override-verdict"
                    legendText="Override verdict"
                    valueSelected={overrideVerdict}
                    onChange={(value) =>
                      setOverrideVerdict(value as 'it_service' | 'single_resource')
                    }
                  >
                    <RadioButton
                      id="it_service"
                      labelText="IT service"
                      value="it_service"
                    />
                    <RadioButton
                      id="single_resource"
                      labelText="Single resource"
                      value="single_resource"
                    />
                  </RadioButtonGroup>
                </div>
              )}

              <div className={styles.formField}>
                <TextArea
                  id="reason"
                  labelText={`Reason (${decision === 'override' ? 'required for override' : 'optional'})`}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                />
              </div>

              <div className={styles.buttonRow}>
                {decision === 'confirm' ? (
                  <Button kind="primary" onClick={handleConfirm} disabled={loading}>
                    Confirm classification
                  </Button>
                ) : (
                  <Button kind="tertiary" onClick={handleOverride} disabled={loading}>
                    Override…
                  </Button>
                )}
              </div>

              <h3 className={styles.sectionHeading}>Decision record</h3>
              <table className={styles.decisionTable}>
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Original verdict</td>
                    <td>
                      {classification.ai_verdict} ({classification.confidence_score.toFixed(2)})
                    </td>
                  </tr>
                  <tr>
                    <td>Override</td>
                    <td>{decision === 'override' ? overrideVerdict : 'None'}</td>
                  </tr>
                  <tr>
                    <td>Final confirmed classification</td>
                    <td>
                      {decision === 'override' ? overrideVerdict : classification.ai_verdict}{' '}
                      (pending confirmation)
                    </td>
                  </tr>
                  <tr>
                    <td>Actor / timestamp</td>
                    <td className={styles.mutedText}>Recorded on submission</td>
                  </tr>
                </tbody>
              </table>
            </div>

        <div className={styles.card}>
              <h2>Routing outcome preview</h2>
              <div className={styles.routingRow}>
                <Tile className={styles.routingTile}>
                  <h3>If IT service</h3>
                  <p>
                    Evidence retrieval, panel mapping, ranked longlist proposal,
                    adjustments, lock and tender dispatch.
                  </p>
                </Tile>
                <Tile className={styles.routingTile}>
                  <h3>If single resource</h3>
                  <p>
                    Vendor Management System handoff. The supplier-selection path for
                    this case is closed after the handoff is registered.
                  </p>
                </Tile>
              </div>
            </div>
      </Stack>
    </div>
  )
}
