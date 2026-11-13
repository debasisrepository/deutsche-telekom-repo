import {
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Button,
  InlineNotification,
} from '@carbon/react';
import { TenderDispatch } from '../../types/dispatch';
import { DispatchStatusBadge } from './DispatchStatusBadge';
import styles from './DispatchTable.module.scss';

interface DispatchTableProps {
  dispatches: TenderDispatch[];
  dispatchBatchId: string;
}

const headers = [
  { key: 'supplier_id', header: 'supplier_id' },
  { key: 'contact', header: 'Contact' },
  { key: 'dispatch_status', header: 'dispatch_status' },
  { key: 'retry_count', header: 'retry_count' },
  { key: 'delivery_confirmation_ref', header: 'delivery_confirmation_ref' },
  { key: 'action', header: 'Action' },
];

export function DispatchTable({ dispatches, dispatchBatchId }: DispatchTableProps) {
  const rows = dispatches.map((d) => ({
    id: d.dispatch_id,
    supplier_id: d.supplier_id,
    contact: d.supplier_contact || 'N/A',
    dispatch_status: d.dispatch_status,
    retry_count: d.retry_count,
    delivery_confirmation_ref: d.delivery_confirmation_ref || 'Pending',
    action: d,
  }));

  const failedCount = dispatches.filter(
    (d) => d.dispatch_status === 'retrying' || d.dispatch_status === 'escalated'
  ).length;
  const deliveredCount = dispatches.filter((d) => d.dispatch_status === 'delivered').length;

  return (
    <div>
      <div className={styles.statsRow}>
        <div className={styles.tile}>
          <span className={styles.label}>dispatch_batch_id</span>
          <span className={styles.mono}>{dispatchBatchId}</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.label}>Tender template</span>
          <span>IT services tender v3</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.label}>Delivered</span>
          <div className={styles.big}>
            {deliveredCount} / {dispatches.length}
          </div>
        </div>
        <div className={styles.tile}>
          <span className={styles.label}>Delivery target</span>
          <div className={styles.big}>99%</div>
        </div>
      </div>

      {failedCount > 0 && (
        <InlineNotification
          kind="warning"
          title={`${failedCount} supplier${failedCount > 1 ? 's' : ''} unreachable or retrying.`}
          subtitle="No supplier is silently dropped. Failed deliveries are retried idempotently, then escalated when retries are exhausted."
          hideCloseButton
          className={styles.notification}
        />
      )}

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
                {rows.map((row) => (
                  <TableRow {...getRowProps({ row })} key={row.id}>
                    {row.cells.map((cell) => {
                      if (cell.info.header === 'supplier_id') {
                        return (
                          <TableCell key={cell.id} className={styles.mono}>
                            {cell.value}
                          </TableCell>
                        );
                      }
                      if (cell.info.header === 'dispatch_status') {
                        return (
                          <TableCell key={cell.id}>
                            <DispatchStatusBadge status={cell.value} />
                          </TableCell>
                        );
                      }
                      if (cell.info.header === 'delivery_confirmation_ref') {
                        return (
                          <TableCell key={cell.id} className={styles.mono}>
                            {cell.value}
                          </TableCell>
                        );
                      }
                      if (cell.info.header === 'action') {
                        const dispatch = cell.value as TenderDispatch;
                        if (dispatch.dispatch_status === 'retrying') {
                          return (
                            <TableCell key={cell.id}>
                              <Button size="sm" kind="tertiary">
                                View attempts
                              </Button>
                            </TableCell>
                          );
                        }
                        if (dispatch.dispatch_status === 'escalated') {
                          return (
                            <TableCell key={cell.id}>
                              <Button size="sm">Update contact and re-dispatch</Button>
                            </TableCell>
                          );
                        }
                        return <TableCell key={cell.id}>-</TableCell>;
                      }
                      return <TableCell key={cell.id}>{cell.value}</TableCell>;
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DataTable>

      {dispatches.some((d) => d.dispatch_status === 'escalated') && (
        <InlineNotification
          kind="error"
          title="Suppliers not delivered after retry exhaustion."
          subtitle="Mailbox rejected the message (stale contact record). The supplier remains on the locked record and is escalated to the Procurement lead."
          hideCloseButton
          className={styles.notificationBottom}
        />
      )}
    </div>
  );
}
