import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button, Tag, DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell } from '@carbon/react'
import { Checkmark, WarningAlt } from '@carbon/icons-react'
import { apiClient } from '../lib/api-client'
import { formatDateTime } from '../lib/utils'
import styles from './EvidenceMappingPage.module.css'

interface Supplier {
  id: number
  supplier_code: string
  display_name: string
  status: string
}

interface EvidenceItem {
  id: number
  case_id: number
  supplier: Supplier | null
  citation_label: string
  citation_ref: string
  evidence_summary: string
  evidence_found: boolean
  created_at: string
}

interface CaseMapping {
  id: number
  panel_code: string
  panel_name: string
  functional_group_code: string
  functional_group_name: string
  mapping_status: string
  rationale_inputs: string
  created_at: string
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
}

interface EvidenceResponse {
  case_id: number
  case_number: string
  evidence_items: EvidenceItem[]
  total: number
}

interface MappingResponse {
  case_id: number
  case_number: string
  mappings: CaseMapping[]
  total: number
}

export function EvidenceMappingPage() {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null)
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([])
  const [mappings, setMappings] = useState<CaseMapping[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!caseId) return

      setIsLoading(true)
      setError(null)
      try {
        const [caseResponse, evidenceResponse, mappingResponse] = await Promise.all([
          apiClient.get<CaseDetail>(`/cases/${caseId}`),
          apiClient.get<EvidenceResponse>(`/cases/${caseId}/evidence`),
          apiClient.get<MappingResponse>(`/cases/${caseId}/mapping`),
        ])

        setCaseDetail(caseResponse)
        setEvidenceItems(evidenceResponse.evidence_items || [])
        setMappings(mappingResponse.mappings || [])
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load data'
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
        <p className={styles.loadingMessage}>Loading evidence and mapping...</p>
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

  const sourceArtifactRef = caseDetail.source_artifacts[0]?.storage_ref || 'N/A'
  const primaryMapping = mappings[0]

  const getWorkflowSteps = () => {
    return [
      { label: 'Intake', description: 'Complete', status: 'done' },
      { label: 'Extraction', description: 'Approved', status: 'done' },
      { label: 'Classification', description: 'IT service (confirmed)', status: 'done' },
      { label: 'Evidence and mapping', description: 'Retrieved', status: 'current' },
      { label: 'Longlist', description: 'Not started', status: 'pending' },
      { label: 'Lock', description: 'Not started', status: 'pending' },
      { label: 'Dispatch', description: 'Not started', status: 'pending' },
    ]
  }

  const steps = getWorkflowSteps()

  const evidenceRows = evidenceItems.map((item) => ({
    id: item.id.toString(),
    supplier: item.supplier?.display_name || 'Unknown Supplier',
    citation_label: item.citation_label,
    citation_ref: item.citation_ref,
    evidence_summary: item.evidence_summary,
    evidence_found: item.evidence_found,
  }))

  const rationaleRows = [
    { id: '1', input: 'Service domain', value: primaryMapping?.rationale_inputs || 'Cloud and container platforms' },
    { id: '2', input: 'Required skills', value: 'Kubernetes, Terraform, GitOps, SRE' },
    { id: '3', input: 'Delivery model', value: 'Team-based, managed outcome' },
  ]

  return (
    <div className={styles.main}>
        <p className={`${styles.breadcrumb} cds--body-compact-01`}>
          <Link to="/" className={styles.breadcrumbLink}>
            Cases
          </Link>{' '}
          /{' '}
          <Link to={`/cases/${caseId}`} className={styles.breadcrumbLink}>
            {caseDetail.case_number}
          </Link>{' '}
          / Evidence and panel mapping
        </p>

        <h1 className={`${styles.pageHeading} cds--productive-heading-05`}>
          Historical supplier evidence and panel mapping
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
              {step.status === 'current' && (
                <span className={styles.ringCurrent} aria-hidden="true" />
              )}
              {step.status === 'pending' && (
                <span className={styles.ring} aria-hidden="true" />
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
              <Tag type="blue">Evidence and mapping ready</Tag>
            </dd>
          </div>
          <div>
            <dt className={`${styles.bannerLabel} cds--label-01`}>Next required action</dt>
            <dd className={styles.bannerValue}>Generate ranked longlist proposal</dd>
          </div>
        </dl>

        <div className={styles.grid}>
          <section className={styles.column10} aria-labelledby="evidence-heading">
            <h2 id="evidence-heading" className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Historical evidence for this case
            </h2>
            <p className={`${styles.helperText} cds--label-01`}>
              Evidence is retrieved from the supplier knowledge base (historical orders and
              commissioned SoWs) and associated with this case. Source status: stub adapter, not yet
              live.
            </p>

            {evidenceRows.length > 0 ? (
              <DataTable
                rows={evidenceRows}
                headers={[
                  { key: 'supplier', header: 'Supplier' },
                  { key: 'citation_label', header: 'Evidence type' },
                  { key: 'citation_ref', header: 'Reference' },
                  { key: 'evidence_summary', header: 'Summary' },
                ]}
              >
                {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                  <Table {...getTableProps()} className={styles.table}>
                    <TableHead>
                      <TableRow>
                        {headers.map((header) => (
                          <TableHeader {...getHeaderProps({ header })} key={header.key}>
                            {header.header}
                          </TableHeader>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {rows.map((row, rowIndex) => {
                        const rowData = evidenceRows[rowIndex]
                        return (
                          <TableRow {...getRowProps({ row })} key={row.id}>
                            <TableCell>{rowData.supplier}</TableCell>
                            <TableCell>
                              <Tag type="teal">
                                {rowData.citation_label.includes('order') ? 'Historical order' : 'Commissioned SoW'}
                              </Tag>
                            </TableCell>
                            <TableCell>
                              <span className={styles.monoText}>{rowData.citation_ref}</span>
                            </TableCell>
                            <TableCell>{rowData.evidence_summary}</TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                )}
              </DataTable>
            ) : (
              <div className={styles.emptyState}>
                <h3 className={`${styles.emptyHeading} cds--productive-heading-01`}>
                  No evidence found
                </h3>
                <p className={styles.mutedText}>
                  No historical order or SoW evidence was found for this case. The outcome is
                  recorded on the case. A supplier without at least one evidence citation cannot be
                  recommended on the longlist.
                </p>
              </div>
            )}

            <div className={styles.emptyState}>
              <h3 className={`${styles.emptyHeading} cds--productive-heading-01`}>
                No-evidence state example · Harz Netzwerktechnik GmbH
              </h3>
              <p className={styles.mutedText}>
                No historical order or SoW evidence was found for this supplier. The outcome is
                recorded on the case. A supplier without at least one evidence citation cannot be
                recommended on the longlist.
              </p>
            </div>
          </section>

          <section className={styles.column6} aria-labelledby="mapping-heading">
            <h2 id="mapping-heading" className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Panel and functional-group mapping
            </h2>

            {primaryMapping ? (
              <>
                <dl className={styles.keyValueList}>
                  <dt>Panel</dt>
                  <dd>
                    <b>{primaryMapping.panel_name}</b>
                  </dd>

                  <dt>Functional group</dt>
                  <dd>
                    <b>{primaryMapping.functional_group_name}</b>
                  </dd>

                  <dt>Mapping status</dt>
                  <dd>
                    <Tag type="green">Mapped</Tag>
                  </dd>
                </dl>

                <h3 className={`${styles.subsectionHeading} cds--productive-heading-01`}>
                  Mapping rationale
                </h3>

                <DataTable
                  rows={rationaleRows}
                  headers={[
                    { key: 'input', header: 'Input' },
                    { key: 'value', header: 'Value' },
                  ]}
                >
                  {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                    <Table {...getTableProps()} className={styles.table}>
                      <TableHead>
                        <TableRow>
                          {headers.map((header) => (
                            <TableHeader {...getHeaderProps({ header })} key={header.key}>
                              {header.header}
                            </TableHeader>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {rows.map((row) => {
                          const rowData = rationaleRows.find((r) => r.id === row.id)
                          return (
                            <TableRow {...getRowProps({ row })} key={row.id}>
                              <TableCell>{rowData?.input}</TableCell>
                              <TableCell>{rowData?.value}</TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                  )}
                </DataTable>
              </>
            ) : (
              <div className={styles.emptyState}>
                <p className={styles.mutedText}>No mapping available for this case.</p>
              </div>
            )}

            <div className={styles.warningNote} role="alert">
              <WarningAlt size={16} className={styles.warningIcon} aria-hidden="true" />
              <div>
                <b>Unmapped example:</b> if no panel matches, the case is flagged "Mapping missing"
                and the reviewer chooses a panel manually.
              </div>
            </div>
          </section>
        </div>

        <div className={styles.actionRow}>
          <Button kind="primary" size="md">
            Generate ranked longlist proposal
          </Button>
          <span className={`${styles.helperText} cds--label-01`}>
            Proposal is produced with an evidence-citation check.
          </span>
        </div>

        <p className={`${styles.footer} cds--label-01`}>
          Wireframe 06 of 08 · Covers FR-011, FR-012, FR-017 · IBM Carbon White theme · Working tier
        </p>
      </div>
  )
}
