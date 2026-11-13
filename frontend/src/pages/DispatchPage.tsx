import { useState, useEffect } from 'react';
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
} from '@carbon/react';
import { apiClient } from '../lib/api-client';
import styles from './DispatchPage.module.scss';

interface TenderDispatch {
  id: string;
  longlist_id: string;
  dispatch_batch_id: string;
  supplier_id: string;
  supplier_contact: string;
  dispatch_status: string;
  retry_count: number;
  delivery_confirmation_ref: string | null;
  error_detail: string | null;
  created_at: string;
  updated_at: string;
}

export function DispatchPage() {
  const [dispatches, setDispatches] = useState<TenderDispatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDispatches = async () => {
      try {
        const response = await apiClient.get<TenderDispatch[]>('/tenders/dispatches');
        const allDispatches: TenderDispatch[] = Array.isArray(response) ? response : [];
        setDispatches(allDispatches);
      } catch (error) {
        console.error('Failed to fetch tender dispatches:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDispatches();
  }, []);

  const getStatusTagType = (status: string): 'green' | 'blue' | 'red' | 'gray' => {
    switch (status) {
      case 'delivered':
        return 'green';
      case 'retrying':
        return 'blue';
      case 'escalated':
        return 'red';
      case 'pending':
      default:
        return 'gray';
    }
  };

  const headers = [
    { key: 'supplier_id', header: 'Supplier ID' },
    { key: 'dispatch_batch_id', header: 'Batch ID' },
    { key: 'dispatch_status', header: 'Status' },
    { key: 'retry_count', header: 'Retry Count' },
    { key: 'delivery_confirmation_ref', header: 'Confirmation Ref' },
    { key: 'error_detail', header: 'Error' },
  ];

  const rows = dispatches.map((dispatch) => ({
    id: dispatch.id,
    supplier_id: dispatch.supplier_id,
    dispatch_batch_id: dispatch.dispatch_batch_id,
    dispatch_status: (
      <Tag type={getStatusTagType(dispatch.dispatch_status)}>
        {dispatch.dispatch_status}
      </Tag>
    ),
    retry_count: dispatch.retry_count,
    delivery_confirmation_ref: dispatch.delivery_confirmation_ref || '—',
    error_detail: dispatch.error_detail || '—',
  }));

  if (loading) {
    return <div className={styles.container}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Tender Dispatch Status</h1>
        <p>
          Monitor tender dispatch delivery status and retry outcomes (ATS12).
        </p>
      </div>

      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <TableContainer title="Tender Dispatches">
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
                    {row.cells.map((cell) => (
                      <TableCell key={cell.id}>{cell.value}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DataTable>
    </div>
  );
}
