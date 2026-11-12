import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  InlineNotification,
  Breadcrumb,
  BreadcrumbItem,
  Grid,
  Column,
  Button,
  Tag,
} from '@carbon/react'
import { CheckmarkFilled, WarningAltFilled } from '@carbon/icons-react'
import { apiClient } from '../lib/api-client'
import { CaseHeader } from '../components/cases/CaseHeader'
import { DispatchStatus } from '../components/longlists/DispatchStatus'
import type { CaseDetail } from '../types/case'
import type {
  LockedLonglist,
  TenderDispatch,
  LonglistProposal,
  RankedSupplier,
} from '../types/longlist'

export function LockDispatchPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseData, setCaseData] = useState<CaseDetail | null>(null)
  const [lockedLonglist, setLockedLonglist] = useState<LockedLonglist | null>(null)
  const [dispatch, setDispatch] = useState<TenderDispatch | null>(null)
  const [suppliers, setSuppliers] = useState<RankedSupplier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDispatching, setIsDispatching] = useState(false)

  useEffect(() => {
    if (!caseId) return
    loadData()
  }, [caseId])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get case data - locked longlist info should be in case response
      const caseResponse = await apiClient.get<CaseDetail>(`/cases/${caseId}`)
      setCaseData(caseResponse)

      // For now, construct locked longlist from case data if available
      // In a real scenario, the backend should return locked_longlist in the case response
      if (caseResponse.workflow_state === 'locked' || caseResponse.workflow_state === 'dispatched') {
        // Mock locked longlist data - in production this would come from backend
        setLockedLonglist({
          locked_longlist_id: 1,
          case_id: Number(caseId),
          source_proposal_id: 1,
          lock_status: 'locked',
          locked_by: 'current_user',
          locked_at: caseResponse.updated_at,
          total_suppliers: 3,
          locked_suppliers: [],
        })
      }

      // Get dispatch if it exists
      try {
        const dispatchResponse = await apiClient.get<TenderDispatch>(
          `/cases/${caseId}/tender-dispatch`
        )
        setDispatch(dispatchResponse)
      } catch {
        // No dispatch yet, that's okay
        setDispatch(null)
      }

      // Get proposal to get supplier details
      try {
        const proposalResponse = await apiClient.post<LonglistProposal>(
          `/cases/${caseId}/longlist-proposals`
        )
        setSuppliers(proposalResponse.items)
      } catch {
        setSuppliers([])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleDispatch = async () => {
    try {
      setIsDispatching(true)
      setError(null)
      const result = await apiClient.post<TenderDispatch>(`/cases/${caseId}/dispatch`, {})
      setDispatch(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to dispatch tender')
    } finally {
      setIsDispatching(false)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  if (error) {
    return (
      <InlineNotification
        kind="error"
        title="Error"
        subtitle={error}
        onCloseButtonClick={() => setError(null)}
      />
    )
  }

  if (!caseData) {
    return <div>Case not found</div>
  }

  const hasDispatch = !!dispatch
  const dispatchStatus = dispatch?.dispatch_status || 'not_started'
  const isPartialFailure = dispatchStatus === 'partial_failure'

  return (
    <div>
      <Breadcrumb>
        <BreadcrumbItem href="/cases">Cases</BreadcrumbItem>
        <BreadcrumbItem href={`/cases/${caseId}`}>{caseData.case_number}</BreadcrumbItem>
        <BreadcrumbItem href="#" isCurrentPage>
          Lock and dispatch
        </BreadcrumbItem>
      </Breadcrumb>

      <h1>{caseData.case_number} · Locked longlist and tender dispatch</h1>

      <ol className="workflow-stepper" aria-label="Case progress">
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Intake</strong>
          <span>Complete</span>
        </li>
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Extraction</strong>
          <span>Approved</span>
        </li>
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Classification</strong>
          <span>IT service (confirmed)</span>
        </li>
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Evidence and mapping</strong>
          <span>Complete</span>
        </li>
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Longlist</strong>
          <span>{lockedLonglist?.total_suppliers || suppliers.length} suppliers · valid</span>
        </li>
        <li className="step-done">
          <CheckmarkFilled className="step-icon" aria-hidden="true" />
          <strong>Lock</strong>
          <span>
            Locked{' '}
            {lockedLonglist ? new Date(lockedLonglist.locked_at).toLocaleString('en-GB', {
              timeZone: 'UTC',
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            }) : 'pending'}
          </span>
        </li>
        <li
          className={isPartialFailure ? 'step-warn' : hasDispatch ? 'step-done' : 'step-current'}
          aria-current={!hasDispatch ? 'step' : undefined}
        >
          {hasDispatch ? (
            isPartialFailure ? (
              <WarningAltFilled className="step-icon" aria-hidden="true" />
            ) : (
              <CheckmarkFilled className="step-icon" aria-hidden="true" />
            )
          ) : (
            <span className="step-ring step-ring-current"></span>
          )}
          <strong>Dispatch</strong>
          <span>{hasDispatch ? dispatchStatus : 'Not started'}</span>
        </li>
      </ol>

      {caseData && (
        <CaseHeader
          caseNumber={caseData.case_number}
          channel={caseData.inbound_channel}
          receivedAt={caseData.created_at}
          needTitle={caseData.normalized_need?.mandatory_fields?.need_title || 'Untitled'}
          sourceArtifact={caseData.source_artifacts?.[0]?.storage_ref}
          workflowState={caseData.workflow_state}
          nextAction={caseData.next_action}
        />
      )}

      {isPartialFailure && (
        <InlineNotification
          kind="warning"
          title="Partial dispatch failure"
          subtitle="Some suppliers received the tender successfully, others failed. Review the recipient table below."
          hideCloseButton
        />
      )}

      <Grid>
        {lockedLonglist && (
          <Column lg={8} md={8} sm={4}>
            <div className="card">
              <h2>Locked longlist snapshot</h2>
              <dl className="info-grid">
                <div>
                  <dt>Total suppliers</dt>
                  <dd>{lockedLonglist.total_suppliers}</dd>
                </div>
                <div>
                  <dt>Locked by</dt>
                  <dd>{lockedLonglist.locked_by}</dd>
                </div>
                <div>
                  <dt>Locked at (UTC)</dt>
                  <dd>
                    {new Date(lockedLonglist.locked_at).toLocaleString('en-GB', {
                      timeZone: 'UTC',
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </dd>
                </div>
              </dl>
              {!hasDispatch && (
                <div style={{ marginTop: '16px' }}>
                  <Button kind="primary" onClick={handleDispatch} disabled={isDispatching}>
                    {isDispatching ? 'Dispatching...' : 'Dispatch tender'}
                  </Button>
                </div>
              )}
            </div>
          </Column>
        )}

        {dispatch && (
          <Column lg={8} md={8} sm={4}>
            <div className="card">
              <h2>Dispatch confirmation</h2>
              <dl className="info-grid">
                <div>
                  <dt>Batch reference</dt>
                  <dd className="mono">{dispatch.dispatch_batch_ref}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>
                    <Tag
                      type={
                        dispatch.dispatch_status === 'success'
                          ? 'green'
                          : dispatch.dispatch_status === 'failed'
                            ? 'red'
                            : 'purple'
                      }
                    >
                      {dispatch.dispatch_status}
                    </Tag>
                  </dd>
                </div>
                <div>
                  <dt>Dispatched by</dt>
                  <dd>{dispatch.dispatched_by}</dd>
                </div>
                <div>
                  <dt>Dispatched at (UTC)</dt>
                  <dd>
                    {new Date(dispatch.dispatched_at).toLocaleString('en-GB', {
                      timeZone: 'UTC',
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </dd>
                </div>
              </dl>
            </div>
          </Column>
        )}

        {dispatch && (
          <Column lg={16} md={8} sm={4}>
            <div className="card">
              <DispatchStatus dispatch={dispatch} suppliers={suppliers} />
            </div>
          </Column>
        )}
      </Grid>
    </div>
  )
}
