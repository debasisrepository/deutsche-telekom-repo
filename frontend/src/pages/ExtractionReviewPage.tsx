import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  InlineNotification,
  Button,
  TextArea,
  Stack,
} from '@carbon/react'
import { apiClient } from '../lib/api-client'
import { CaseDetail } from '../types/case'
import {
  ExtractionReviewPayload,
  ExtractionReviewDecisionRequest,
  ReviewDecisionResponse,
} from '../types/review'
import { CaseHeader } from '../components/cases/CaseHeader'
import { WorkflowStepper } from '../components/cases/WorkflowStepper'
import { ExtractionReviewTable } from '../components/reviews/ExtractionReviewTable'
import styles from './ExtractionReviewPage.module.css'

export function ExtractionReviewPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null)
  const [extractionPayload, setExtractionPayload] =
    useState<ExtractionReviewPayload | null>(null)
  const [editedAttributes, setEditedAttributes] = useState<ExtractionReviewPayload>({})
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadCase() {
      if (!caseId) return
      try {
        const detail = await apiClient.get<CaseDetail>(`/cases/${caseId}`)
        setCaseDetail(detail)

        // Mock extraction payload - in production, fetch from backend
        const mockPayload: ExtractionReviewPayload = {
          'Service scope': {
            value: 'Operate and develop managed Kubernetes platform',
            source_excerpt:
              'p.4 §2.1 "Operation and further development…"',
            confidence: 0.93,
            lineage: 'ai_generated',
          },
          Duration: {
            value: '24 months',
            source_excerpt: 'p.5 "Laufzeit: 24 Monate, Option 12 Monate"',
            confidence: 0.71,
            lineage: 'ai_generated',
          },
          'Required skills': {
            value: ['Kubernetes', 'Terraform', 'GitOps', 'SRE'],
            source_excerpt: 'p.4 §2.3',
            confidence: 0.95,
            lineage: 'ai_generated',
          },
          'Delivery model': {
            value: 'Team-based, managed outcome',
            source_excerpt: 'p.4 §2.1',
            confidence: 0.88,
            lineage: 'ai_generated',
          },
          Location: {
            value: 'Bonn / remote',
            source_excerpt: 'p.5 §3.2',
            lineage: 'directly_sourced',
          },
          'Planned start': {
            value: '2027-01-11',
            source_excerpt: 'p.5 "Leistungsbeginn"',
            lineage: 'directly_sourced',
          },
          Coverage: {
            value: '24/7 on-call',
            source_excerpt: 'p.4 §2.3',
            confidence: 0.9,
            lineage: 'ai_generated',
          },
        }
        setExtractionPayload(mockPayload)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load case')
      }
    }
    loadCase()
  }, [caseId])

  const handleAttributeEdit = (attributeName: string, value: string) => {
    if (!extractionPayload) return

    setEditedAttributes((prev) => ({
      ...prev,
      [attributeName]: {
        ...extractionPayload[attributeName],
        value,
        lineage: 'human_corrected',
        confidence: 1.0,
      },
    }))
  }

  const handleApprove = async () => {
    if (!caseId) return
    setLoading(true)
    setError(null)
    try {
      const request: ExtractionReviewDecisionRequest = {
        decision: 'approve',
      }
      await apiClient.post<ReviewDecisionResponse>(
        `/cases/${caseId}/reviews/extraction`,
        request
      )
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve extraction')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAndApprove = async () => {
    if (!caseId || Object.keys(editedAttributes).length === 0) return
    setLoading(true)
    setError(null)
    try {
      const request: ExtractionReviewDecisionRequest = {
        decision: 'edit',
        edited_attributes: editedAttributes,
      }
      await apiClient.post<ReviewDecisionResponse>(
        `/cases/${caseId}/reviews/extraction`,
        request
      )
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save edits')
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async () => {
    if (!caseId) return
    setLoading(true)
    setError(null)
    try {
      const request: ExtractionReviewDecisionRequest = {
        decision: 'reject',
      }
      await apiClient.post<ReviewDecisionResponse>(
        `/cases/${caseId}/reviews/extraction`,
        request
      )
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject extraction')
    } finally {
      setLoading(false)
    }
  }

  if (!caseDetail || !extractionPayload) {
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
        Extraction review
      </nav>

      <Stack gap={5}>
        <h1>Extraction review gate</h1>

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
          title="Human approval required (AMBER gate)."
          subtitle="The extraction below was proposed by the system. It cannot advance to classification until a reviewer approves, edits or rejects it. Review SLA: 1 business day."
          hideCloseButton
        />

        <section className={styles.card}>
          <h2>Extracted attributes</h2>
          <ExtractionReviewTable
            attributes={extractionPayload}
            editedAttributes={editedAttributes}
            onAttributeEdit={handleAttributeEdit}
          />
          <p className={styles.helperText}>
            Generated values stay distinguishable from human-edited values; both
            versions are kept in the case record.
          </p>
        </section>

        <section className={styles.card}>
          <h2>Source context</h2>
          <p className={styles.label}>
            DT-IT-RFP_Cloud-Platform-Engineering_v3.pdf · page 5
          </p>
          <div className={styles.sourceDoc}>
            <p>
              <strong>3.1 Term.</strong>{' '}
              <mark>Laufzeit: 24 Monate</mark>, plus an option to extend by 12
              months.
            </p>
            <p>
              <strong>3.2 Place of performance.</strong> Bonn; remote work by
              agreement.
            </p>
          </div>
        </section>

        <section className={styles.gateSection}>
          <h2>Review decision</h2>
          <div className={styles.formField}>
            <TextArea
              id="comment"
              labelText="Reviewer comment (required for edit or reject)"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
            />
          </div>
          <div className={styles.buttonRow}>
            <Button kind="primary" onClick={handleApprove} disabled={loading}>
              Approve as is
            </Button>
            <Button
              kind="secondary"
              onClick={handleSaveAndApprove}
              disabled={loading || Object.keys(editedAttributes).length === 0}
            >
              Save edits and approve
            </Button>
            <Button kind="danger" onClick={handleReject} disabled={loading}>
              Reject extraction
            </Button>
          </div>
        </section>

        <p className={styles.helperText}>
          Audit: decision, actor and timestamp are recorded with the resulting attribute
          set. No decision has been recorded yet.
        </p>
      </Stack>
    </div>
  )
}
