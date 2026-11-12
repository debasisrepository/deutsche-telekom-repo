import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Theme, Button, DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, Tag } from '@carbon/react'
import { CaseHeader } from '../components/cases/CaseHeader'
import { WorkflowStepper } from '../components/cases/WorkflowStepper'
import { apiClient } from '../lib/api-client'
import { formatDateTime } from '../lib/utils'
import type { CaseDetail } from '../types/case'
import styles from './CaseOverviewPage.module.css'

export function CaseOverviewPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadCase = async () => {
      if (!caseId) return

      setIsLoading(true)
      setError(null)
      try {
        const response = await apiClient.get<CaseDetail>(`/cases/${caseId}`)
        setCaseDetail(response)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load case'
        setError(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }

    loadCase()
  }, [caseId])

  if (isLoading) {
    return (
      <Theme theme="white">
        <main className={styles.main} id="main-content">
          <p className={styles.loadingMessage}>Loading case details...</p>
        </main>
      </Theme>
    )
  }

  if (error || !caseDetail) {
    return (
      <Theme theme="white">
        <main className={styles.main} id="main-content">
          <p className={styles.errorMessage}>
            {error || 'Case not found'}
          </p>
          <Link to="/" className={styles.errorLink}>
            Back to cases
          </Link>
        </main>
      </Theme>
    )
  }

  const normalizedNeed = caseDetail.normalized_need
  const mandatoryFields = normalizedNeed?.mandatory_fields || {}
  const completenessScore = normalizedNeed?.completeness_score || 0
  const mandatoryFieldsComplete = Math.round((completenessScore * 10))
  const totalMandatoryFields = 10

  const normalizedNeedRows = [
    {
      id: '1',
      field: 'Need title *',
      value: mandatoryFields.need_title || 'Not provided in source',
      mapped: 'p.1 · "Subject"',
      origin: mandatoryFields.need_title ? 'Directly sourced' : 'Missing',
    },
    {
      id: '2',
      field: 'Requesting unit *',
      value: mandatoryFields.business_unit || 'Not provided in source',
      mapped: 'p.1 · "Auftraggeber"',
      origin: mandatoryFields.business_unit ? 'Directly sourced' : 'Missing',
    },
    {
      id: '3',
      field: 'Service domain *',
      value: 'Cloud and container platforms',
      mapped: 'p.3 · "Leistungsbeschreibung"',
      origin: 'Derived',
    },
    {
      id: '4',
      field: 'Delivery model *',
      value: 'Team-based delivery, managed outcome',
      mapped: 'p.4 · 2.1',
      origin: 'Derived',
    },
    {
      id: '5',
      field: 'Planned start *',
      value: '2027-01-11',
      mapped: 'p.5 · "Leistungsbeginn"',
      origin: 'Directly sourced',
    },
    {
      id: '6',
      field: 'Duration *',
      value: '24 months',
      mapped: 'p.5 · "Laufzeit"',
      origin: 'Directly sourced',
    },
    {
      id: '7',
      field: 'Location *',
      value: 'Bonn / remote',
      mapped: 'p.5 · 3.2',
      origin: 'Directly sourced',
    },
    {
      id: '8',
      field: 'Required skills *',
      value: 'Kubernetes, Terraform, GitOps, SRE',
      mapped: 'p.4 · 2.3',
      origin: 'Derived',
    },
    {
      id: '9',
      field: 'Security level *',
      value: 'Confidential internal',
      mapped: 'p.2 · 1.4',
      origin: 'Directly sourced',
    },
    {
      id: '10',
      field: 'Budget reference *',
      value: 'Not provided in source',
      mapped: '–',
      origin: 'Missing',
    },
  ]

  const getOriginTag = (origin: string) => {
    if (origin === 'Missing') return <Tag type="red">Missing</Tag>
    if (origin === 'Directly sourced') return <Tag type="gray">Directly sourced</Tag>
    if (origin === 'Derived') return <Tag type="purple">Derived</Tag>
    return null
  }

  const sourceArtifactRef = caseDetail.source_artifacts[0]?.storage_ref || 'N/A'

  return (
    <Theme theme="white">
      <main className={styles.main} id="main-content">
        <p className={`${styles.breadcrumb} cds--body-compact-01`}>
          <Link to="/" className={styles.breadcrumbLink}>
            Cases
          </Link>{' '}
          / {caseDetail.case_number} / Overview
        </p>

        <CaseHeader
          caseNumber={caseDetail.case_number}
          channel={caseDetail.inbound_channel}
          receivedAt={caseDetail.created_at}
          needTitle={mandatoryFields.need_title?.toString() || 'Untitled need'}
          sourceArtifact={sourceArtifactRef}
          workflowState={caseDetail.workflow_state}
          nextAction={caseDetail.next_action}
        />

        <WorkflowStepper workflowState={caseDetail.workflow_state} />

        <div className={styles.buttonGroup}>
          <Button kind="primary" size="md">Open extraction review</Button>
          <Button kind="tertiary" size="md">View source artifact</Button>
        </div>

        <div className={styles.grid}>
          <section className={styles.column11}>
            <h2 className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Normalized need record
            </h2>

            <div className={styles.completenessRow}>
              <span className={`${styles.completenessLabel} cds--label-01`}>
                Mandatory fields complete: {mandatoryFieldsComplete} of {totalMandatoryFields}
              </span>
              <Tag type="green">Normalization complete</Tag>
            </div>

            <div
              className={styles.progressBar}
              role="progressbar"
              aria-valuenow={mandatoryFieldsComplete * 10}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Mandatory field completeness"
              style={{ '--progress-width': `${mandatoryFieldsComplete * 10}%` } as React.CSSProperties}
            >
              <div className={styles.progressFill} />
            </div>

            <DataTable rows={normalizedNeedRows} headers={[
              { key: 'field', header: 'Field' },
              { key: 'value', header: 'Normalized value' },
              { key: 'mapped', header: 'Mapped from raw submission' },
              { key: 'origin', header: 'Origin' },
            ]}>
              {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                <Table {...getTableProps()}>
                  <TableHead>
                    <TableRow>
                      {headers.map((header) => (
                        <TableHeader {...getHeaderProps({ header })}>
                          {header.header}
                        </TableHeader>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row, index) => {
                      const rowData = normalizedNeedRows[index]
                      return (
                        <TableRow {...getRowProps({ row })}>
                          <TableCell>{rowData.field}</TableCell>
                          <TableCell className={rowData.origin === 'Missing' ? styles.valueSecondary : ''}>
                            {rowData.value}
                          </TableCell>
                          <TableCell>
                            <span className={styles.channelText}>
                              {rowData.mapped}
                            </span>
                          </TableCell>
                          <TableCell>{getOriginTag(rowData.origin)}</TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              )}
            </DataTable>

            <p className={`${styles.helperText} cds--label-01`}>
              * Mandatory normalized field. Missing fields are tracked for completeness; further missing-information
              handling is outside this increment.
            </p>
          </section>

          <section className={styles.column5}>
            <h2 className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Preserved source artifact
            </h2>

            <div className={styles.documentBox}>
              <p className={`${styles.documentLabel} cds--label-01`}>
                {sourceArtifactRef} · page 4
              </p>
              <p className={styles.documentParagraph}>
                <b>2.1 Scope.</b>{' '}
                <mark className={styles.documentHighlight}>
                  Operation and further development of the managed Kubernetes platform
                </mark>{' '}
                for Magenta Cloud Core by a dedicated supplier team.
              </p>
              <p className={styles.documentParagraph}>
                <b>2.3 Qualifications.</b>{' '}
                <mark className={styles.documentHighlight}>
                  Kubernetes, Terraform, GitOps, SRE practices
                </mark>
                ; on-call coverage 24/7.
              </p>
            </div>

            <h3 className={`${styles.subsectionHeading} cds--productive-heading-01`}>
              Case history
            </h3>

            <ul className={styles.historyList}>
              <li className={styles.historyItem}>
                <b>Case created</b>
                <br />
                <span className={`${styles.historyLabel} cds--label-01`}>
                  {formatDateTime(caseDetail.created_at)} · system (AGN5) · initial state set
                </span>
              </li>
              <li className={styles.historyItem}>
                <b>Normalized record created</b>
                <br />
                <span className={`${styles.historyLabel} cds--label-01`}>
                  {formatDateTime(caseDetail.updated_at)} · system (AGN5)
                </span>
              </li>
              <li className={styles.historyItem}>
                <b>Awaiting extraction review</b>
                <br />
                <span className={`${styles.historyLabel} cds--label-01`}>
                  {formatDateTime(caseDetail.updated_at)} · assigned to Need-Intake Reviewer
                </span>
              </li>
            </ul>
          </section>
        </div>

        <p className={`${styles.footer} cds--label-01`}>
          Wireframe 02 of 08 · Covers FR-001, FR-002, FR-003 · IBM Carbon White theme · Working tier
        </p>
      </main>
    </Theme>
  )
}
