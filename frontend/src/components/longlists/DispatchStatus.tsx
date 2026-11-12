import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, Tag, Tile } from '@carbon/react'
import type { TenderDispatch, RankedSupplier } from '../../types/longlist'

interface DispatchStatusProps {
  dispatch: TenderDispatch
  suppliers: RankedSupplier[]
}

export function DispatchStatus({ dispatch, suppliers }: DispatchStatusProps) {
  const deliveredCount = dispatch.recipients.filter((r) => r.delivery_status === 'success').length
  const failedCount = dispatch.recipients.filter((r) => r.delivery_status === 'failed').length

  const supplierMap = new Map(suppliers.map((s) => [s.supplier_id, s]))

  const headers = [
    { key: 'rank', header: 'Rank' },
    { key: 'supplier', header: 'Supplier' },
    { key: 'delivery_status', header: 'Delivery status' },
    { key: 'external_delivery_ref', header: 'External delivery ref' },
    { key: 'last_attempt_at', header: 'Last attempt (UTC)' },
  ]

  const rows = dispatch.recipients.map((recipient) => ({
    id: recipient.recipient_id.toString(),
    ...recipient,
    supplier: supplierMap.get(recipient.supplier_id),
  }))

  return (
    <div className="dispatch-status-section">
      <h2>Per-supplier dispatch outcome</h2>

      <div className="dispatch-summary">
        <Tile>
          <span className="dispatch-summary-label">Dispatch status</span>
          <strong className="dispatch-summary-value">{dispatch.dispatch_status}</strong>
        </Tile>
        <Tile>
          <span className="dispatch-summary-label">Delivered</span>
          <strong className="dispatch-summary-value">
            {deliveredCount} of {dispatch.total_recipients}
          </strong>
        </Tile>
        <Tile>
          <span className="dispatch-summary-label">Failed</span>
          <strong className="dispatch-summary-value">{failedCount}</strong>
        </Tile>
      </div>

      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps }) => (
          <Table {...getTableProps()} aria-label="Dispatch outcomes per supplier">
            <TableHead>
              <TableRow>
                {headers.map((header) => (
                  <TableHeader key={header.key}>{header.header}</TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const rowData = row as unknown as typeof dispatch.recipients[0] & {
                  id: string
                  supplier?: RankedSupplier
                }
                const supplier = rowData.supplier
                const isFailed = rowData.delivery_status === 'failed'

                return (
                  <TableRow key={row.id} className={isFailed ? 'cds--data-table--selected' : ''}>
                    <TableCell>{supplier?.rank_position || '—'}</TableCell>
                    <TableCell>{supplier?.supplier_name || 'Unknown'}</TableCell>
                    <TableCell>
                      <Tag type={rowData.delivery_status === 'success' ? 'green' : 'red'} size="sm">
                        {rowData.delivery_status}
                      </Tag>
                    </TableCell>
                    <TableCell className="monospace-cell">
                      {rowData.external_delivery_ref || '—'}
                    </TableCell>
                    <TableCell>
                      {rowData.last_attempt_at
                        ? new Date(rowData.last_attempt_at).toLocaleString('en-GB', {
                            timeZone: 'UTC',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : '—'}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </DataTable>

      <p className="dispatch-batch-info">
        Batch reference <span className="monospace-text">{dispatch.dispatch_batch_ref}</span> ·
        dispatched by {dispatch.dispatched_by} at{' '}
        {new Date(dispatch.dispatched_at).toLocaleString('en-GB', {
          timeZone: 'UTC',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        })}{' '}
        UTC.
      </p>
    </div>
  )
}
