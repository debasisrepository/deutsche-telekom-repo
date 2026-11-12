import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  InlineNotification,
  Breadcrumb,
  BreadcrumbItem,
  Grid,
  Column,
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  type DataTableHeader,
} from '@carbon/react'
import { CheckmarkFilled } from '@carbon/icons-react'
import { apiClient } from '../lib/api-client'
import { CaseHeader } from '../components/cases/CaseHeader'
import { LonglistTable } from '../components/longlists/LonglistTable'
import { AdjustmentForm } from '../components/longlists/AdjustmentForm'
import { ValidationBand } from '../components/longlists/ValidationBand'
import type { CaseDetail } from '../types/case'
import type { LonglistProposal, RankedSupplier, ValidationResult } from '../types/longlist'

interface AdjustmentHistoryRow {
  id: string
  when: string
  actor: string
  change: string
  rationale: string
  count_after: number
}

export function LonglistAdjustmentsPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState<CaseDetail | null>(null)
  const [proposal, setProposal] = useState<LonglistProposal | null>(null)
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRevalidating, setIsRevalidating] = useState(false)
  const [isLocking, setIsLocking] = useState(false)

  useEffect(() => {
    if (!caseId) return
    loadData()
  }, [caseId])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [caseResponse, proposalResponse] = await Promise.all([
        apiClient.get<CaseDetail>(`/cases/${caseId}`),
        apiClient.post<LonglistProposal>(`/cases/${caseId}/longlist-proposals`),
      ])

      setCaseData(caseResponse)
      setProposal(proposalResponse)

      // Try to get existing validation
      try {
        const validationResponse = await apiClient.get<ValidationResult>(
          `/cases/${caseId}/validations/supplier-count/latest`
        )
        setValidation(validationResponse)
      } catch {
        // No validation exists yet, that's okay
        setValidation(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleAdjustment = async (adjustment: {
    supplier_id: number
    change_type: 'add' | 'remove'
    rationale: string
  }) => {
    try {
      await apiClient.post(`/cases/${caseId}/adjustments`, adjustment)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record adjustment')
    }
  }

  const handleRevalidate = async () => {
    try {
      setIsRevalidating(true)
      setError(null)
      const result = await apiClient.post<ValidationResult>(
        `/cases/${caseId}/validations/supplier-count`
      )
      setValidation(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate')
    } finally {
      setIsRevalidating(false)
    }
  }

  const handleLock = async () => {
    if (!validation || validation.validation_result !== 'valid') {
      return
    }

    try {
      setIsLocking(true)
      setError(null)
      await apiClient.post(`/cases/${caseId}/lock`, {})
      navigate(`/cases/${caseId}/lock-dispatch`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to lock longlist')
    } finally {
      setIsLocking(false)
    }
  }

  const handleRemoveSupplier = async (supplier: RankedSupplier) => {
    await handleAdjustment({
      supplier_id: supplier.supplier_id,
      change_type: 'remove',
      rationale: `Removing ${supplier.supplier_name} from longlist`,
    })
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

  if (!caseData || !proposal) {
    return <div>Case or proposal not found</div>
  }

  const currentCount = proposal.items.length

  // Build adjustment history rows - for now just show initial proposal
  const adjustmentHistoryRows: AdjustmentHistoryRow[] = [
    {
      id: 'initial',
      when: new Date(proposal.created_at).toLocaleString('en-GB', {
        timeZone: 'UTC',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      }),
      actor: 'System (AGN2)',
      change: 'Proposal',
      rationale: 'Generated from evidence and panel mapping',
      count_after: currentCount,
    },
  ]

  const adjustmentHistoryHeaders: DataTableHeader[] = [
    { key: 'when', header: 'When (UTC)' },
    { key: 'actor', header: 'Actor' },
    { key: 'change', header: 'Change' },
    { key: 'rationale', header: 'Rationale' },
    { key: 'count_after', header: 'Count after' },
  ]

  return (
    <div>
      <Breadcrumb>
        <BreadcrumbItem href="/cases">Cases</BreadcrumbItem>
        <BreadcrumbItem href={`/cases/${caseId}`}>{caseData.case_number}</BreadcrumbItem>
        <BreadcrumbItem href="#" isCurrentPage>
          Longlist
        </BreadcrumbItem>
      </Breadcrumb>

      <h1>Ranked longlist, adjustments and validation</h1>

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
        <li className="step-current" aria-current="step">
          <span className="step-ring step-ring-current"></span>
          <strong>Longlist</strong>
          <span>Adjusting · count {validation?.validation_result || 'not validated'}</span>
        </li>
        <li className="step-pending">
          <span className="step-ring"></span>
          <strong>Lock</strong>
          <span>Blocked</span>
        </li>
        <li className="step-pending">
          <span className="step-ring"></span>
          <strong>Dispatch</strong>
          <span>Not started</span>
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

      <InlineNotification
        kind="warning"
        title="Human approval required (AMBER gate)."
        subtitle="The proposal is generated by the system; the case manager reviews, adjusts and then locks it. Generated entries and human adjustments are marked separately."
        hideCloseButton
      />

      <Grid>
        <Column lg={11} md={8} sm={4}>
          <div className="card">
            <h2>Longlist proposal · {currentCount} suppliers</h2>
            <LonglistTable
              suppliers={proposal.items}
              onRemove={handleRemoveSupplier}
            />
            <InlineNotification
              kind="warning"
              title="Citation rule:"
              subtitle="every recommended supplier needs at least one evidence citation. A supplier without citations cannot be added as 'recommended' – the add control reports 'No evidence found for this supplier'."
              hideCloseButton
            />
          </div>
        </Column>

        <Column lg={5} md={8} sm={4}>
          <div className="card">
            <ValidationBand
              validation={validation}
              currentCount={currentCount}
              onRevalidate={handleRevalidate}
              onLock={handleLock}
              isRevalidating={isRevalidating}
              isLocking={isLocking}
            />
          </div>
        </Column>

        <Column lg={6} md={8} sm={4}>
          <div className="card">
            <h2>Add or remove supplier</h2>
            <AdjustmentForm
              suppliers={proposal.items.map((s) => ({
                supplier_id: s.supplier_id,
                supplier_name: s.supplier_name,
              }))}
              onSubmit={handleAdjustment}
            />
          </div>
        </Column>

        <Column lg={10} md={8} sm={4}>
          <div className="card">
            <h2>Adjustment history</h2>
            <DataTable
              rows={adjustmentHistoryRows}
              headers={adjustmentHistoryHeaders}
            >
              {({ rows, headers, getTableProps }) => (
                <Table {...getTableProps()} aria-label="Supplier adjustment history">
                  <TableHead>
                    <TableRow>
                      {headers.map((header) => (
                        <TableHeader key={header.key}>{header.header}</TableHeader>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row) => {
                      const adj = adjustmentHistoryRows.find((a) => a.id === row.id)
                      if (!adj) return null
                      return (
                        <TableRow key={row.id}>
                          <TableCell>{adj.when}</TableCell>
                          <TableCell>{adj.actor}</TableCell>
                          <TableCell>
                            <Tag
                              type={
                                adj.change === 'add'
                                  ? 'green'
                                  : adj.change === 'remove'
                                    ? 'red'
                                    : 'purple'
                              }
                              size="sm"
                            >
                              {adj.change}
                            </Tag>
                          </TableCell>
                          <TableCell>{adj.rationale}</TableCell>
                          <TableCell>{adj.count_after}</TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              )}
            </DataTable>
          </div>
        </Column>
      </Grid>
    </div>
  )
}
