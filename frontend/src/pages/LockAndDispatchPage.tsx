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
  ProgressIndicator,
  ProgressStep,
  InlineNotification,
} from '@carbon/react';
import { Checkmark, WarningAlt } from '@carbon/icons-react';
import { LockDetail } from '../components/dispatch/LockDetail';
import { DispatchTable } from '../components/dispatch/DispatchTable';
import { Longlist } from '../types/governance';
import { TenderDispatch } from '../types/dispatch';
import styles from './LockAndDispatchPage.module.scss';

interface LockedSupplier {
  id: string;
  rank: number;
  supplier_id: string;
  supplier_name: string;
  origin: string;
  membership: string;
}

export function LockAndDispatchPage() {
  const { longlistId } = useParams<{ longlistId: string }>();
  const [longlist, setLonglist] = useState<Longlist | null>(null);
  const [dispatches, setDispatches] = useState<TenderDispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (longlistId) {
      loadLockAndDispatchData(longlistId);
    }
  }, [longlistId]);

  const loadLockAndDispatchData = async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock data based on wireframe 08 and handoff file
      const mockLonglist: Longlist = {
        longlist_id: id,
        need_id: 'NEED-2024-0402',
        proposal_id: 'PRP-2024-0402-01',
        suppliers: ['SUP-0231', 'SUP-0118', 'SUP-0045', 'SUP-0518', 'SUP-0412'],
        locked: true,
        locked_at: '2024-11-12T13:20:44Z',
        locked_by: 'Longlist Finalization Owner',
        validation_verdict_at_lock: 'pass',
        change_history: [
          {
            action: 'add',
            timestamp: '2024-11-12T11:00:00Z',
            actor: 'bu.cloudops.lead',
            supplier_id: 'SUP-0518',
            reason: 'BU requests additional niche provider',
          },
          {
            action: 'remove',
            timestamp: '2024-11-12T11:10:00Z',
            actor: 'bu.cloudops.lead',
            supplier_id: 'SUP-0307',
            reason: 'Overlapping capability with SUP-0412',
          },
          {
            action: 'lock',
            timestamp: '2024-11-12T13:20:44Z',
            actor: 'Longlist Finalization Owner',
            supplier_ids: ['SUP-0231', 'SUP-0118', 'SUP-0045', 'SUP-0518', 'SUP-0412'],
            validation_verdict: 'pass',
          },
        ],
        created_at: '2024-11-12T10:00:00Z',
        updated_at: '2024-11-12T13:20:44Z',
      };

      const mockDispatches: TenderDispatch[] = [
        {
          dispatch_id: 'disp-001',
          longlist_id: id,
          dispatch_batch_id: 'DSP-2024-0402-01',
          supplier_id: 'SUP-0231',
          supplier_contact: 'tenders@supplier-a.example',
          dispatch_status: 'delivered',
          retry_count: 0,
          delivery_confirmation_ref: 'CONF-77120',
          error_detail: null,
          escalation_opened: false,
          last_attempt_at: '2024-11-12T13:25:00Z',
          created_at: '2024-11-12T13:25:00Z',
          updated_at: '2024-11-12T13:25:00Z',
        },
        {
          dispatch_id: 'disp-002',
          longlist_id: id,
          dispatch_batch_id: 'DSP-2024-0402-01',
          supplier_id: 'SUP-0118',
          supplier_contact: 'vertrieb@supplier-b.example',
          dispatch_status: 'delivered',
          retry_count: 0,
          delivery_confirmation_ref: 'CONF-77121',
          error_detail: null,
          escalation_opened: false,
          last_attempt_at: '2024-11-12T13:25:00Z',
          created_at: '2024-11-12T13:25:00Z',
          updated_at: '2024-11-12T13:25:00Z',
        },
        {
          dispatch_id: 'disp-003',
          longlist_id: id,
          dispatch_batch_id: 'DSP-2024-0402-01',
          supplier_id: 'SUP-0045',
          supplier_contact: 'bids@supplier-c.example',
          dispatch_status: 'delivered',
          retry_count: 1,
          delivery_confirmation_ref: 'CONF-77124',
          error_detail: null,
          escalation_opened: false,
          last_attempt_at: '2024-11-12T13:26:00Z',
          created_at: '2024-11-12T13:25:00Z',
          updated_at: '2024-11-12T13:26:00Z',
        },
        {
          dispatch_id: 'disp-004',
          longlist_id: id,
          dispatch_batch_id: 'DSP-2024-0402-01',
          supplier_id: 'SUP-0518',
          supplier_contact: 'office@supplier-d.example',
          dispatch_status: 'retrying',
          retry_count: 2,
          delivery_confirmation_ref: null,
          error_detail: 'Temporary email server unavailable, retrying',
          escalation_opened: false,
          last_attempt_at: '2024-11-12T13:30:00Z',
          created_at: '2024-11-12T13:25:00Z',
          updated_at: '2024-11-12T13:30:00Z',
        },
        {
          dispatch_id: 'disp-005',
          longlist_id: id,
          dispatch_batch_id: 'DSP-2024-0402-01',
          supplier_id: 'SUP-0412',
          supplier_contact: 'contact@supplier-e.example (stale)',
          dispatch_status: 'escalated',
          retry_count: 3,
          delivery_confirmation_ref: null,
          error_detail: 'Retry exhausted after 3 attempts, escalated to manual intervention',
          escalation_opened: true,
          last_attempt_at: '2024-11-12T13:35:00Z',
          created_at: '2024-11-12T13:25:00Z',
          updated_at: '2024-11-12T13:35:00Z',
        },
      ];

      setLonglist(mockLonglist);
      setDispatches(mockDispatches);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load lock and dispatch data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading description="Loading lock and dispatch data..." withOverlay />;
  }

  if (error) {
    return <div className={styles.error}>Error: {error}</div>;
  }

  if (!longlist) {
    return <div className={styles.error}>Longlist not found</div>;
  }

  const lockedSuppliers: LockedSupplier[] = [
    {
      id: '1',
      rank: 1,
      supplier_id: 'SUP-0231',
      supplier_name: 'Telemark Cloud Services',
      origin: 'Cloud and hosting panel',
      membership: 'locked',
    },
    {
      id: '2',
      rank: 2,
      supplier_id: 'SUP-0118',
      supplier_name: 'Rheinland Infrastructure',
      origin: 'Cloud and hosting panel',
      membership: 'locked',
    },
    {
      id: '3',
      rank: 3,
      supplier_id: 'SUP-0045',
      supplier_name: 'Sovereign Stack GmbH',
      origin: 'Cloud and hosting panel',
      membership: 'locked',
    },
    {
      id: '4',
      rank: 4,
      supplier_id: 'SUP-0518',
      supplier_name: 'Nordlicht Secure Cloud GmbH',
      origin: 'Niche research (accepted)',
      membership: 'locked',
    },
    {
      id: '5',
      rank: 5,
      supplier_id: 'SUP-0412',
      supplier_name: 'Migrate AG',
      origin: 'Added by BU (adj. 2)',
      membership: 'locked',
    },
  ];

  const supplierHeaders = [
    { key: 'rank', header: 'Rank' },
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'supplier_name', header: 'Supplier' },
    { key: 'origin', header: 'Origin' },
    { key: 'membership', header: 'Membership' },
  ];

  return (
    <div className={styles.page}>
      <p className={styles.breadcrumb}>
        Longlists / {longlist.longlist_id} / Lock and tender dispatch
      </p>

      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>Finalize and lock longlist, then dispatch tender</h1>
          <p className={styles.lead}>
            A longlist is locked only after it passes count validation. Once locked, supplier membership is immutable
            and is the sole basis for tender dispatch to every listed supplier, with per-supplier delivery confirmation.
          </p>
        </div>
        <div className={styles.tags}>
          <Tag type="green">ATS11 - GREEN</Tag>
          <Tag type="green">ATS12 - GREEN</Tag>
          <Tag>AGN3 / AGN5 / TOL4 / TOL6</Tag>
        </div>
      </div>

      <ProgressIndicator currentIndex={3} className={styles.progressIndicator}>
        <ProgressStep label="ATS9 Count validated: pass (5)" description="done" complete />
        <ProgressStep label="ATS10 Adjustments captured (2)" description="done, revalidated" complete />
        <ProgressStep label="ATS11 Locked" description={`${longlist.longlist_id}, immutable`} complete />
        <ProgressStep label="ATS12 Tender dispatch" description="in progress" current />
      </ProgressIndicator>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>ATS11 Locked longlist record</h2>

        <div className={styles.gridRow}>
          <LockDetail longlist={longlist} />
          <div className={styles.card}>
            <h3 className={styles.heading}>Pre-lock checks (all passed)</h3>
            <div className={styles.check}>
              <Checkmark className={styles.checkIcon} />
              Supplier count 5 within 3 to 6 (ATS9 rerun after last change)
            </div>
            <div className={styles.check}>
              <Checkmark className={styles.checkIcon} />
              Each supplier has a cited evidence source or research citation
            </div>
            <div className={styles.check}>
              <Checkmark className={styles.checkIcon} />
              Audit-log write succeeded for the lock commit
            </div>
            <InlineNotification
              kind="error"
              title="Blocked actions."
              subtitle="Lock is refused on commit failure, rule failure or audit-log write failure. A tender dispatched against an unlocked or modified list is blocked."
              hideCloseButton
              className={styles.notification}
            />
          </div>
        </div>

        <p className={styles.annotation}>
          Wireframe sample data: supplier names and contacts are fictitious and shown for layout only.
        </p>

        <DataTable rows={lockedSuppliers} headers={supplierHeaders}>
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
                        if (cell.info.header === 'membership') {
                          return (
                            <TableCell key={cell.id}>
                              <Tag>{cell.value}</Tag>
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
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>ATS12 Tender package and dispatch</h2>
        <DispatchTable dispatches={dispatches} dispatchBatchId="DSP-2024-0402-01" />

        <div className={`${styles.gridRow} ${styles.gridRowSpaced}`}>
          <div className={styles.card}>
            <h3 className={styles.heading}>Dispatch readiness gates</h3>
            <div className={styles.check}>
              <Checkmark className={styles.checkIcon} />
              Longlist is locked and compliant
            </div>
            <div className={styles.check}>
              <Checkmark className={styles.checkIcon} />
              Longlist is not empty
            </div>
            <div className={styles.check}>
              <WarningAlt className={styles.errorIcon} />
              1 supplier has invalid contact data (SUP-0412)
            </div>
          </div>
          <div className={styles.card}>
            <div className={styles.actions}>
              <Button>Retry failed dispatches</Button>
              <Button kind="tertiary">View audit trail</Button>
            </div>
            <p className={styles.helpText}>
              Per-supplier confirmation or failure state is stored for every attempt and is available to audit reporting.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LockAndDispatchPage;
