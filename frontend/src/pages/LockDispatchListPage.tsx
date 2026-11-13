import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Tag,
} from '@carbon/react';
import { apiClient } from '../lib/api-client';
import styles from './LockDispatchListPage.module.scss';

interface Need {
  id: string;
  business_unit_id: string;
  classification_verdict: string;
  status: string;
}

export function LockDispatchListPage() {
  const [needs, setNeeds] = useState<Need[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNeeds = async () => {
      try {
        const response = await apiClient.get<Need[]>('/intake/needs?limit=100');
        const allNeeds: Need[] = Array.isArray(response) ? response : [];
        // Filter for needs that would have locked longlists
        const itServiceNeeds = allNeeds.filter(
          (need: Need) => need.classification_verdict === 'it_service'
        );
        setNeeds(itServiceNeeds);
      } catch (error) {
        console.error('Failed to fetch needs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNeeds();
  }, []);

  const handleViewLockDispatch = (needId: string) => {
    // Navigate to lock-dispatch page with a longlist ID
    // In a real scenario, we'd map need_id to longlist_id via API
    // For now, use a constructed longlist ID
    const longlistId = `LL-${needId.split('-').pop()}`;
    navigate(`/lock-dispatch/${longlistId}`);
  };

  const headers = [
    { key: 'need_id', header: 'Need ID' },
    { key: 'business_unit_id', header: 'Business Unit' },
    { key: 'classification_verdict', header: 'Classification' },
    { key: 'locked_status', header: 'Lock Status' },
    { key: 'actions', header: 'Actions' },
  ];

  const rows = needs.map((need) => ({
    id: need.id,
    need_id: need.id,
    business_unit_id: need.business_unit_id,
    classification_verdict: (
      <Tag type="blue">{need.classification_verdict}</Tag>
    ),
    locked_status: <Tag type="green">Locked</Tag>,
    actions: (
      <Button
        size="sm"
        kind="tertiary"
        onClick={() => handleViewLockDispatch(need.id)}
      >
        View Lock & Dispatch
      </Button>
    ),
  }));

  if (loading) {
    return <div className={styles.container}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Lock & Dispatch Management</h1>
        <p>
          Review locked longlists and tender dispatch status (ATS11, ATS12).
        </p>
      </div>

      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <TableContainer title="Locked Longlists">
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
