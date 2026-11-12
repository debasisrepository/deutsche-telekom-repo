import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  Pagination,
} from '@carbon/react'
import { apiClient } from '../lib/api-client'
import { CaseListItem } from '../types/case'
import { formatDateTime, getStatusBadgeColor } from '../lib/utils'
import styles from './CasesListPage.module.css'

export function CasesListPage() {
  const [cases, setCases] = useState<CaseListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadCases() {
      setLoading(true)
      setError(null)
      try {
        const response = await apiClient.get<{
          items: CaseListItem[]
          total: number
          page: number
          page_size: number
        }>(`/cases?page=${page}&page_size=${pageSize}`)
        setCases(response.items)
        setTotal(response.total)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cases')
      } finally {
        setLoading(false)
      }
    }
    loadCases()
  }, [page, pageSize])

  const headers = [
    { key: 'case_number', header: 'Case number' },
    { key: 'channel', header: 'Channel' },
    { key: 'need_title', header: 'Need title' },
    { key: 'workflow_state', header: 'Status' },
    { key: 'created_at', header: 'Created' },
  ]

  const rows = cases.map((c) => ({
    id: c.id.toString(),
    case_number: c.case_number,
    channel: c.inbound_channel,
    need_title: 'Untitled',
    workflow_state: c.workflow_state,
    created_at: formatDateTime(c.created_at),
  }))

  if (loading && cases.length === 0) {
    return <div>Loading cases...</div>
  }

  if (error) {
    return <div>Error: {error}</div>
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>All Cases</h1>
      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <TableContainer>
            <Table {...getTableProps()}>
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
                  const caseItem = cases.find((c) => c.id.toString() === row.id)
                  return (
                    <TableRow {...getRowProps({ row })} key={row.id}>
                      <TableCell>
                        <Link to={`/cases/${caseItem?.id}`}>{row.cells[0].value}</Link>
                      </TableCell>
                      <TableCell>{row.cells[1].value}</TableCell>
                      <TableCell>{row.cells[2].value}</TableCell>
                      <TableCell>
                        <Tag type={getStatusBadgeColor(row.cells[3].value as string) as 'red' | 'green' | 'blue' | 'gray'}>
                          {row.cells[3].value}
                        </Tag>
                      </TableCell>
                      <TableCell>{row.cells[4].value}</TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DataTable>
      <Pagination
        totalItems={total}
        page={page}
        pageSize={pageSize}
        pageSizes={[10, 20, 50]}
        onChange={({ page, pageSize }) => {
          setPage(page)
          setPageSize(pageSize)
        }}
      />
    </div>
  )
}
