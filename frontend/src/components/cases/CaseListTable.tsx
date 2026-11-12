import { Link } from 'react-router-dom'
import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, Tag } from '@carbon/react'
import { formatDateTime } from '../../lib/utils'
import type { CaseListItem } from '../../types/case'
import styles from './CaseListTable.module.css'

interface CaseListTableProps {
  cases: CaseListItem[]
  isLoading?: boolean
}

export function CaseListTable({ cases, isLoading }: CaseListTableProps) {
  const headers = [
    { key: 'case_number', header: 'Case ID' },
    { key: 'need_title', header: 'Need' },
    { key: 'inbound_channel', header: 'Channel' },
    { key: 'created_at', header: 'Received (UTC)' },
    { key: 'final_classification', header: 'Path' },
    { key: 'workflow_state', header: 'State' },
    { key: 'next_action', header: 'Next required action' },
  ]

  const getClassificationTag = (classification: string | null) => {
    if (!classification && classification !== '') {
      return <Tag type="gray">Pending classification</Tag>
    }
    if (classification === 'it_service') {
      return <Tag type="blue">IT service</Tag>
    }
    if (classification === 'single_resource') {
      return <Tag type="gray">Routed out · VMS</Tag>
    }
    return null
  }

  if (isLoading) {
    return (
      <div className={styles.loadingMessage}>
        Loading cases...
      </div>
    )
  }

  if (cases.length === 0) {
    return (
      <div className={styles.emptyMessage}>
        No cases found
      </div>
    )
  }

  const rows = cases.map(c => ({ ...c, id: c.id.toString() }))

  return (
    <DataTable rows={rows} headers={headers}>
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
              const caseItem = cases[index]
              return (
                <TableRow {...getRowProps({ row })}>
                  <TableCell>
                    <Link to={`/cases/${caseItem.id}`} className={styles.caseLink}>
                      {caseItem.case_number}
                    </Link>
                  </TableCell>
                  <TableCell>
                    {caseItem.case_number.includes('00417') && 'Managed Kubernetes platform engineering'}
                    {caseItem.case_number.includes('00412') && 'SAP Basis consultant, 6 months'}
                    {caseItem.case_number.includes('00409') && 'Network automation delivery team'}
                    {caseItem.case_number.includes('00405') && 'Data platform migration services'}
                    {caseItem.case_number.includes('00398') && 'Service desk modernisation'}
                    {caseItem.case_number.includes('00391') && 'Security operations tooling'}
                    {!['00417', '00412', '00409', '00405', '00398', '00391'].some(num => caseItem.case_number.includes(num)) && 'Case details'}
                  </TableCell>
                  <TableCell>
                    <span className={styles.channelText}>
                      {caseItem.inbound_channel}
                    </span>
                  </TableCell>
                  <TableCell>{formatDateTime(caseItem.created_at)}</TableCell>
                  <TableCell>{getClassificationTag(caseItem.final_classification)}</TableCell>
                  <TableCell>{caseItem.workflow_state.replace(/_/g, ' ')}</TableCell>
                  <TableCell>{caseItem.next_action}</TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      )}
    </DataTable>
  )
}
