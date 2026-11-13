import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  TableContainer,
  Button,
  Loading,
} from '@carbon/react';
import { View } from '@carbon/icons-react';
import { apiClient } from '../lib/api-client';
import styles from './EvidenceListPage.module.scss';

interface Need {
  id: string;
  business_unit_id: string;
  status: string;
  classification_verdict: string | null;
  arrival_timestamp: string;
}

interface NeedsResponse {
  items: Need[];
}

const headers = [
  { key: 'id', header: 'Need ID' },
  { key: 'business_unit_id', header: 'Business Unit' },
  { key: 'classification_verdict', header: 'Classification' },
  { key: 'status', header: 'Status' },
  { key: 'arrival_timestamp', header: 'Arrival' },
  { key: 'actions', header: 'Actions' },
];

export function EvidenceListPage() {
  const [needs, setNeeds] = useState<Need[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNeeds = async () => {
      try {
        const response = await apiClient.get<Need[]>('/intake/needs');
        // Filter to classified IT service needs that can have evidence
        const classifiedNeeds = Array.isArray(response) ? response.filter(
          (need: Need) => need.classification_verdict === 'it_service'
        ) : [];
        setNeeds(classifiedNeeds);
      } catch (error) {
        console.error('Failed to fetch needs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNeeds();
  }, []);

  const rows = needs.map((need) => ({
    id: need.id,
    business_unit_id: need.business_unit_id,
    classification_verdict: need.classification_verdict || '-',
    status: need.status,
    arrival_timestamp: new Date(need.arrival_timestamp).toLocaleString(),
    actions: (
      <Button
        kind="ghost"
        size="sm"
        renderIcon={View}
        iconDescription="View evidence"
        onClick={() => navigate(`/evidence/${need.id}`)}
      >
        View Evidence
      </Button>
    ),
  }));

  if (loading) {
    return <Loading description="Loading needs..." />;
  }

  return (
    <div>
      <h1 className={`cds--type-productive-heading-04 ${styles.pageHeading}`}>
        Evidence
      </h1>
      <p className={`cds--type-body-01 ${styles.pageDescription}`}>
        View historical supplier evidence and panel mappings for classified IT service needs.
      </p>
      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <TableContainer title="Classified IT Service Needs">
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
