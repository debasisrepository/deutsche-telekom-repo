import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Button,
  Tag,
  InlineNotification,
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  ProgressIndicator,
  ProgressStep,
} from '@carbon/react';
import { Locked } from '@carbon/icons-react';
import { apiClient } from '../lib/api-client';
import type { Need } from '../types/need';
import './VmsHandoffPage.scss';

interface HandoffAttemptRow {
  id: string;
  need_id: string;
  attempt: string;
  result: string;
  confirmation: string;
  escalation: string;
  action: string;
}

export function VmsHandoffPage() {
  const { needId } = useParams<{ needId: string }>();
  const navigate = useNavigate();
  const [need, setNeed] = useState<Need | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!needId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const needData = await apiClient.get<Need>(`/intake/needs/${needId}`);
        setNeed(needData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load VMS handoff data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [needId]);

  if (loading) {
    return (
      <div className="vms-handoff-page">
        <p>Loading VMS handoff status...</p>
      </div>
    );
  }

  if (error && !need) {
    return (
      <div className="vms-handoff-page">
        <InlineNotification
          kind="error"
          title="Error"
          subtitle={error}
          lowContrast
        />
      </div>
    );
  }

  if (!need) {
    return (
      <div className="vms-handoff-page">
        <p>Need not found</p>
      </div>
    );
  }

  const isTerminal = need.status === 'vms_routed_terminal';
  const handoffConfirmed = isTerminal;

  return (
    <div className="vms-handoff-page">
      <div className="vms-handoff-page__breadcrumb">
        Need queue / {need.id} / ATS4 VMS handoff
      </div>

      <div className="vms-handoff-page__header">
        <div>
          <h1 className="vms-handoff-page__title">VMS Handoff</h1>
          <p className="vms-handoff-page__lead">
            After a reviewed single_resource verdict the normalized Need record is sent one way to the Vendor Management System. 
            The handoff is terminal: this case never enters the longlist flow.
          </p>
        </div>
        <div className="vms-handoff-page__tags">
          <Tag type="green">ATS4 - GREEN deterministic</Tag>
          <Tag type="gray">AGN5 / TOL5</Tag>
          <Tag type="gray">Write-only outbound, service account</Tag>
        </div>
      </div>

      <ProgressIndicator currentIndex={3} className="vms-handoff-page__progress">
        <ProgressStep label="ATS1 Normalized" description="done" complete />
        <ProgressStep label="ATS2 Attributes reviewed" description="done" complete />
        <ProgressStep label="ATS3 Classified single_resource (reviewed)" description="done" complete />
        <ProgressStep label="ATS4 VMS handoff" description="completed, workflow terminal" current />
      </ProgressIndicator>

      {handoffConfirmed && (
        <InlineNotification
          kind="success"
          title="Handoff confirmed."
          subtitle={`${need.id} was accepted by the Vendor Management System in 6.2 s (limit 30 s). The supplier-selection workflow is closed for this case.`}
          lowContrast
        />
      )}

      <div className="vms-handoff-page__grid">
        <section>
          <h2 className="vms-handoff-page__section-title">Handoff result</h2>
          <div className="vms-handoff-page__card">
            <dl className="vms-handoff-page__dl">
              <dt>need_id</dt>
              <dd className="vms-handoff-page__mono">{need.id}</dd>
              
              <dt>classification_verdict</dt>
              <dd>
                <Tag type="red">single_resource</Tag> reviewed by IT Procurement, confidence {need.classification_confidence?.toFixed(2) || '0.96'}
              </dd>
              
              <dt>Reviewed rationale</dt>
              <dd>One named senior Java developer, 12 months, staff-augmentation framing</dd>
              
              <dt>handover_confirmation</dt>
              <dd><Tag type={handoffConfirmed ? 'green' : 'gray'}>{handoffConfirmed ? 'true' : 'false'}</Tag></dd>
              
              <dt>vms_reference_id</dt>
              <dd className="vms-handoff-page__mono">VMS-2024-118302</dd>
              
              <dt>Handoff timestamp (UTC)</dt>
              <dd className="vms-handoff-page__mono">2024-11-12T09:41:27Z</dd>
              
              <dt>workflow_status</dt>
              <dd><Tag type="gray">{need.status}</Tag></dd>
              
              <dt>Correlation ID</dt>
              <dd className="vms-handoff-page__mono">{need.correlation_id}</dd>
            </dl>

            <div className="vms-handoff-page__actions">
              <Button kind="tertiary">View audit trail</Button>
              <Button kind="secondary" onClick={() => navigate('/needs')}>
                Back to need queue
              </Button>
            </div>
          </div>
        </section>

        <section>
          <h2 className="vms-handoff-page__section-title">Workflow gates after handoff</h2>
          <div className="vms-handoff-page__card">
            <span className="vms-handoff-page__label">Blocked steps for this case</span>
            <div className="vms-handoff-page__blocked">
              <Tag type="gray" renderIcon={Locked}>ATS5</Tag>
              <Tag type="gray">ATS6</Tag>
              <Tag type="gray">ATS7</Tag>
              <Tag type="gray">ATS8</Tag>
              <Tag type="gray">ATS9</Tag>
              <Tag type="gray">ATS10</Tag>
              <Tag type="gray">ATS11</Tag>
              <Tag type="gray">ATS12</Tag>
            </div>
            <p className="vms-handoff-page__help">
              ATS5 to ATS12 are unavailable. Re-entry requires an explicit, reviewed reclassification through a governed restart.
            </p>
            <div className="vms-handoff-page__actions">
              <Button disabled>Open longlist research (ATS5)</Button>
            </div>
          </div>

          <h3 className="vms-handoff-page__subsection-title">Requester view</h3>
          <InlineNotification
            kind="info"
            title="The business unit BU-NETWORK is notified with VMS-2024-118302 for follow-up outside this process."
            lowContrast
          />
        </section>
      </div>

      <section>
        <h2 className="vms-handoff-page__section-title">
          Failed handoff example: escalation, no silent loss
        </h2>
        <InlineNotification
          kind="error"
          title="VMS handoff failed for NEED-2024-0405."
          subtitle="TOL5 returned a timeout after 30 s. The request is held with error status and escalated to the Procurement lead. It is not dropped and not moved to the longlist flow."
          lowContrast
        />
        <DataTable
          rows={[
            { id: '1', need_id: 'NEED-2024-0405', attempt: '1 of 3', result: 'error', confirmation: 'false', escalation: 'Procurement lead notified 09:44', action: 'retry' },
            { id: '2', need_id: 'NEED-2024-0391', attempt: '1 of 3', result: 'confirmed', confirmation: 'true', escalation: 'None', action: 'view' },
          ] as HandoffAttemptRow[]}
          headers={[
            { key: 'need_id', header: 'need_id' },
            { key: 'attempt', header: 'Attempt' },
            { key: 'result', header: 'Result' },
            { key: 'confirmation', header: 'handover_confirmation' },
            { key: 'escalation', header: 'Escalation' },
            { key: 'action', header: 'Action' },
          ]}
        >
          {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
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
                      <TableCell 
                        key={cell.id}
                        className={(cell.info.header === 'need_id' || cell.info.header === 'handover_confirmation') ? 'vms-handoff-page__mono' : ''}
                      >
                        {cell.info.header === 'result' ? (
                          <Tag type={cell.value === 'error' ? 'red' : 'green'}>
                            {cell.value === 'error' ? 'error: timeout' : 'confirmed'}
                          </Tag>
                        ) : cell.info.header === 'action' ? (
                          <Button size="sm" kind={cell.value === 'retry' ? 'primary' : 'tertiary'}>
                            {cell.value === 'retry' ? 'Retry handoff' : 'View'}
                          </Button>
                        ) : (
                          cell.value
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </DataTable>
      </section>
    </div>
  );
}
