import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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
import { CountVisualization } from '../components/governance/CountVisualization';
import { ValidationHistory } from '../components/governance/ValidationHistory';
import { AdjustmentForm } from '../components/governance/AdjustmentForm';
import { apiClient } from '../lib/api-client';
import { Longlist, LonglistAdjustment } from '../types/governance';
import styles from './ValidationAndAdjustmentPage.module.scss';

interface ValidationRun {
  id: string;
  run: number;
  trigger: string;
  count: number;
  verdict: 'pass' | 'fail';
}

interface CurrentSupplier {
  id: string;
  rank: number;
  supplier_id: string;
  panel_source: string;
  status: string;
}

export function ValidationAndAdjustmentPage() {
  const { longlistId } = useParams<{ longlistId: string }>();
  const [longlist, setLonglist] = useState<Longlist | null>(null);
  const [adjustments, setAdjustments] = useState<LonglistAdjustment[]>([]);
  const [validationRuns, setValidationRuns] = useState<ValidationRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (longlistId) {
      loadLonglistData(longlistId);
    }
  }, [longlistId]);

  const loadLonglistData = async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      // Fetch longlist data - in real scenario this would be from a GET endpoint
      // For now, we'll construct mock data based on the wireframe
      const mockLonglist: Longlist = {
        longlist_id: id,
        need_id: 'NEED-2024-0418',
        proposal_id: 'PRP-2024-0418-01',
        suppliers: ['SUP-0231', 'SUP-0045'],
        locked: false,
        locked_at: null,
        locked_by: null,
        validation_verdict_at_lock: null,
        change_history: [
          {
            action: 'remove',
            timestamp: '2024-11-12T11:02:00Z',
            actor: 'bu.cloudops.lead',
            supplier_id: 'SUP-0307',
            reason: 'Capacity conflict with running project',
          },
          {
            action: 'remove',
            timestamp: '2024-11-12T11:09:00Z',
            actor: 'bu.cloudops.lead',
            supplier_id: 'SUP-0118',
            reason: 'Prior delivery dispute',
          },
          {
            action: 'remove',
            timestamp: '2024-11-12T11:15:00Z',
            actor: 'bu.cloudops.lead',
            supplier_id: 'SUP-0518',
            reason: 'Scope not confirmed in time',
          },
        ],
        created_at: '2024-11-12T10:00:00Z',
        updated_at: '2024-11-12T11:15:00Z',
      };

      const mockValidationRuns: ValidationRun[] = [
        { id: '1', run: 1, trigger: 'Proposal received (ATS8)', count: 5, verdict: 'pass' },
        { id: '2', run: 2, trigger: 'After adjustment 1', count: 4, verdict: 'pass' },
        { id: '3', run: 3, trigger: 'After adjustment 2', count: 3, verdict: 'pass' },
        { id: '4', run: 4, trigger: 'After adjustment 3', count: 2, verdict: 'fail' },
      ];

      setLonglist(mockLonglist);
      setAdjustments(
        mockLonglist.change_history.map((ch, idx) => ({
          adjustment_id: `adj-${idx + 1}`,
          longlist_id: id,
          supplier_id: ch.supplier_id || '',
          action: ch.action as 'add' | 'remove',
          reason: ch.reason || '',
          actor: ch.actor,
          timestamp: ch.timestamp,
        }))
      );
      setValidationRuns(mockValidationRuns);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load longlist data');
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustmentSubmit = async (
    supplierId: string,
    action: 'add' | 'remove',
    reason: string
  ) => {
    if (!longlistId) return;

    await apiClient.post(`/longlists/${longlistId}/adjustments`, {
      supplier_id: supplierId,
      action,
      reason,
      actor: 'bu.cloudops.lead',
    });

    // Reload data after successful adjustment (apiClient throws on errors)
    await loadLonglistData(longlistId);
  };

  const currentSuppliers: CurrentSupplier[] = longlist
    ? [
        {
          id: '1',
          rank: 1,
          supplier_id: 'SUP-0231',
          panel_source: 'Cloud and hosting panel',
          status: 'On list',
        },
        {
          id: '2',
          rank: 3,
          supplier_id: 'SUP-0045',
          panel_source: 'Cloud and hosting panel',
          status: 'On list',
        },
        {
          id: '3',
          rank: 2,
          supplier_id: 'SUP-0118',
          panel_source: 'Cloud and hosting panel',
          status: 'Removed by BU (adj. 2)',
        },
        {
          id: '4',
          rank: 4,
          supplier_id: 'SUP-0518',
          panel_source: 'Niche research',
          status: 'Removed by BU (adj. 3)',
        },
        {
          id: '5',
          rank: 5,
          supplier_id: 'SUP-0307',
          panel_source: 'Platform engineering panel',
          status: 'Removed by BU (adj. 1)',
        },
      ]
    : [];

  const supplierHeaders = [
    { key: 'rank', header: 'Rank' },
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'panel_source', header: 'panel_source' },
    { key: 'status', header: 'Status' },
  ];

  const changeHistoryHeaders = [
    { key: 'number', header: '#' },
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'action', header: 'action' },
    { key: 'reason', header: 'reason' },
    { key: 'actor', header: 'actor' },
    { key: 'timestamp', header: 'timestamp (UTC)' },
  ];

  const changeHistoryRows = adjustments.map((adj, idx) => ({
    id: adj.adjustment_id,
    number: idx + 1,
    supplier_id: adj.supplier_id,
    action: adj.action,
    reason: adj.reason,
    actor: adj.actor,
    timestamp: new Date(adj.timestamp).toISOString().replace('T', ' ').substring(0, 16),
  }));

  if (loading) {
    return <Loading description="Loading longlist data..." withOverlay />;
  }

  if (error) {
    return <div className={styles.error}>Error: {error}</div>;
  }

  if (!longlist) {
    return <div className={styles.error}>Longlist not found</div>;
  }

  const currentCount = longlist.suppliers.length;
  const validationVerdict: 'pass' | 'fail' = currentCount >= 3 && currentCount <= 6 ? 'pass' : 'fail';

  return (
    <div className={styles.page}>
      <p className={styles.breadcrumb}>
        Longlists / {longlist.longlist_id} / Count validation and business-unit alignment
      </p>

      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>Validate supplier count and capture business-unit adjustments</h1>
          <p className={styles.lead}>
            The supplier-count rule is a hard gate: fewer than 3 or more than 6 suppliers fails and blocks lock and dispatch.
            Business-unit add and remove requests are recorded with a reason, then the count is validated again.
          </p>
        </div>
        <div className={styles.tags}>
          <Tag type="green">ATS9 - GREEN gate</Tag>
          <Tag type="green">ATS10 - GREEN capture</Tag>
          <Tag>AGN3 / AGN5 / TOL4</Tag>
        </div>
      </div>

      <div className={styles.caseBar}>
        <div>
          <span className={styles.label}>longlist_id</span>
          <span className={styles.mono}>{longlist.longlist_id}</span>
        </div>
        <div>
          <span className={styles.label}>proposal_id</span>
          <span className={styles.mono}>{longlist.proposal_id}</span>
        </div>
        <div>
          <span className={styles.label}>need_id</span>
          <span className={styles.mono}>{longlist.need_id}</span>
        </div>
        <div>
          <span className={styles.label}>locked</span>
          <Tag>{longlist.locked ? 'true' : 'false'}</Tag>
        </div>
        <div>
          <span className={styles.label}>Business unit contact</span>
          <span>BU-CLOUD-OPS representative</span>
        </div>
      </div>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>ATS9 Supplier-count validation</h2>
        <div className={styles.gridRow}>
          <CountVisualization currentCount={currentCount} validationVerdict={validationVerdict} />
          <ValidationHistory validationRuns={validationRuns} />
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>ATS10 Business-unit adjustments</h2>
        <div className={styles.gridRow75}>
          <div>
            <div className={styles.toolbar}>
              <span>Current suppliers ({currentCount})</span>
              <Tag>Change history attached to record</Tag>
            </div>
            <DataTable rows={currentSuppliers} headers={supplierHeaders}>
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
                            if (cell.info.header === 'status') {
                              const isRemoved = String(cell.value).includes('Removed');
                              return (
                                <TableCell key={cell.id}>
                                  <Tag type={isRemoved ? 'red' : 'green'}>{cell.value}</Tag>
                                </TableCell>
                              );
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

            <h3 className={styles.subheading}>Change history (LonglistAdjustment)</h3>
            <DataTable rows={changeHistoryRows} headers={changeHistoryHeaders}>
              {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                <TableContainer>
                  <Table {...getTableProps()} className={styles.smallTable}>
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
                            if (cell.info.header === 'supplier_id' || cell.info.header === 'timestamp') {
                              return (
                                <TableCell key={cell.id} className={styles.mono}>
                                  {cell.value}
                                </TableCell>
                              );
                            }
                            if (cell.info.header === 'action') {
                              return (
                                <TableCell key={cell.id}>
                                  <span className={cell.value === 'add' ? styles.add : styles.rem}>
                                    {cell.value}
                                  </span>
                                </TableCell>
                              );
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
          </div>

          <AdjustmentForm actor="bu.cloudops.lead" onSubmit={handleAdjustmentSubmit} />
        </div>

        <div className={styles.actions}>
          <Button disabled={validationVerdict !== 'pass'}>Continue to lock (ATS11)</Button>
          <span className={styles.helpText}>
            {validationVerdict !== 'pass' && 'Disabled until validation_verdict = pass.'}
          </span>
        </div>
      </section>
    </div>
  );
}

export default ValidationAndAdjustmentPage;
