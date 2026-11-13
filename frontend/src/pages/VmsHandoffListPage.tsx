import { useEffect, useState } from 'react';
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
  Tag,
  Button,
  Loading,
} from '@carbon/react';
import { View } from '@carbon/icons-react';
import { apiClient } from '../lib/api-client';
import './VmsHandoffListPage.scss';

interface VmsHandoff {
  need_id: string;
  classification_verdict: string;
  handover_confirmation: boolean;
  vms_reference_id: string | null;
  workflow_status: string;
  created_at: string;
}

interface VmsHandoffListResponse {
  handoffs: VmsHandoff[];
  total: number;
}

const headers = [
  { key: 'need_id', header: 'Need ID' },
  { key: 'classification_verdict', header: 'Classification' },
  { key: 'handover_confirmation', header: 'Handoff Status' },
  { key: 'vms_reference_id', header: 'VMS Reference' },
  { key: 'workflow_status', header: 'Workflow Status' },
  { key: 'actions', header: 'Actions' },
];

export function VmsHandoffListPage() {
  const navigate = useNavigate();
  const [handoffs, setHandoffs] = useState<VmsHandoff[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHandoffs = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<VmsHandoffListResponse>('/integrations/vms/handoffs');
        setHandoffs(response.handoffs || []);
      } catch (err) {
        console.error('Failed to fetch VMS handoffs:', err);
        setError('Failed to load VMS handoffs');
      } finally {
        setLoading(false);
      }
    };

    fetchHandoffs();
  }, []);

  const rows = handoffs.map((handoff) => ({
    id: handoff.need_id,
    need_id: handoff.need_id,
    classification_verdict: (
      <Tag type={handoff.classification_verdict === 'single_resource' ? 'red' : 'blue'}>
        {handoff.classification_verdict}
      </Tag>
    ),
    handover_confirmation: (
      <Tag type={handoff.handover_confirmation ? 'green' : 'red'}>
        {handoff.handover_confirmation ? 'Confirmed' : 'Failed'}
      </Tag>
    ),
    vms_reference_id: handoff.vms_reference_id || '—',
    workflow_status: (
      <Tag type="gray">{handoff.workflow_status}</Tag>
    ),
    actions: (
      <Button
        kind="ghost"
        size="sm"
        renderIcon={View}
        iconDescription="View details"
        onClick={() => navigate(`/vms-handoff/${handoff.need_id}`)}
      >
        View
      </Button>
    ),
  }));

  if (loading) {
    return (
      <div className="vms-handoff-list-page__loading-container">
        <Loading description="Loading VMS handoffs..." withOverlay={false} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="vms-handoff-list-page__error-container">
        <Tag type="red">{error}</Tag>
      </div>
    );
  }

  return (
    <div className="vms-handoff-list-page">
      <h1 className="vms-handoff-list-page__header">VMS Handoff</h1>
      <p className="vms-handoff-list-page__lead">
        Single-resource needs routed to the Vendor Management System
      </p>
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
      {handoffs.length === 0 && (
        <div className="vms-handoff-list-page__empty-state">
          No VMS handoffs found
        </div>
      )}
    </div>
  );
}
