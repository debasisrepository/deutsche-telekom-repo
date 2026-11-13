import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Button,
  RadioButton,
  RadioButtonGroup,
  TextArea,
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  InlineNotification,
} from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import { apiClient } from '../lib/api-client';
import { ClassificationCard } from '../components/review/ClassificationCard';
import { ExemplarTable } from '../components/review/ExemplarTable';
import type { Need } from '../types/need';
import type { ClassificationReviewRequest, ClassificationReviewResponse } from '../types/classification';
import './ClassificationReviewPage.scss';

interface Exemplar {
  id: string;
  verdict: 'single_resource' | 'it_service';
  similarity: number;
  description: string;
}

interface RubricRow {
  id: string;
  verdict: string;
  rubric: string;
  route: string;
}

interface QueueRow {
  id: string;
  need_id: string;
  proposed: string;
  confidence: string;
  state: string;
}

export function ClassificationReviewPage() {
  const { needId } = useParams<{ needId: string }>();
  const navigate = useNavigate();
  const [need, setNeed] = useState<Need | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewDecision, setReviewDecision] = useState<'approve' | 'modify' | 'reject'>('approve');
  const [verdict, setVerdict] = useState<'single_resource' | 'it_service'>('it_service');
  const [rationale, setRationale] = useState('Programme-style scope with deliverables; no individual role. Confirmed it_service.');

  const exemplars: Exemplar[] = [
    { id: 'EX-0212 Sovereign cloud migration', verdict: 'it_service', similarity: 0.91, description: 'Sovereign cloud migration' },
    { id: 'EX-0187 SAP S/4 rollout wave 2', verdict: 'it_service', similarity: 0.84, description: 'SAP S/4 rollout wave 2' },
    { id: 'EX-0150 One senior Java developer', verdict: 'single_resource', similarity: 0.22, description: 'One senior Java developer' },
  ];

  useEffect(() => {
    if (!needId) return;

    const fetchNeed = async () => {
      try {
        setLoading(true);
        const data = await apiClient.get<Need>(`/intake/needs/${needId}`);
        setNeed(data);
        
        if (data.classification_verdict) {
          setVerdict(data.classification_verdict as 'single_resource' | 'it_service');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load need');
      } finally {
        setLoading(false);
      }
    };

    fetchNeed();
  }, [needId]);

  const handleSubmit = async () => {
    if (!needId || !need) return;

    try {
      setSubmitting(true);
      setError(null);

      const request: ClassificationReviewRequest = {
        review_decision: reviewDecision,
        classification_verdict: reviewDecision === 'modify' ? verdict : (need.classification_verdict as 'single_resource' | 'it_service') || verdict,
        classification_confidence: need.classification_confidence || 0.93,
        rationale,
        exemplars_referenced: exemplars.map(e => e.id),
        escalation_required: (need.classification_confidence || 0) < 0.70,
      };

      const response = await apiClient.post<ClassificationReviewResponse>(
        `/reviews/needs/${needId}/classification`,
        request
      );

      if (response.next_workflow_status === 'classified_single_resource') {
        navigate('/reviews');
      } else if (response.next_workflow_status === 'classified_it_service') {
        navigate('/reviews');
      } else {
        navigate('/reviews');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit classification review');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="classification-review-page">
        <p>Loading classification review...</p>
      </div>
    );
  }

  if (error && !need) {
    return (
      <div className="classification-review-page">
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
      <div className="classification-review-page">
        <p>Need not found</p>
      </div>
    );
  }

  return (
    <div className="classification-review-page">
      <div className="classification-review-page__breadcrumb">
        Review workbench / {need.id} / ATS3 classification review
      </div>

      <div className="classification-review-page__header">
        <div>
          <h1 className="classification-review-page__title">Classification Review</h1>
          <p className="classification-review-page__lead">
            The classifier works only from the reviewed attribute set and the documented rubric. 
            Borderline or low-confidence cases are held for review and can never be auto-routed to the Vendor Management System.
          </p>
        </div>
        <div className="classification-review-page__tags">
          <Tag type="warm-gray">ATS3 - AMBER human review</Tag>
          <Tag type="gray">AGN1 / Classify Need Type</Tag>
          <Tag type="gray">workflow_status: classification_review_pending</Tag>
        </div>
      </div>

      <div className="classification-review-page__casebar">
        <div>
          <span className="classification-review-page__label">need_id</span>
          <span className="classification-review-page__mono">{need.id}</span>
        </div>
        <div>
          <span className="classification-review-page__label">business_unit_id</span>
          {need.business_unit_id}
        </div>
        <div>
          <span className="classification-review-page__label">Attributes</span>
          Reviewed at ATS2 by reviewer, 12 Nov 2024 09:02
        </div>
        <div>
          <span className="classification-review-page__label">Review SLA</span>
          3 h 12 min remaining
        </div>
      </div>

      <div className="classification-review-page__grid">
        <section>
          <h2 className="classification-review-page__section-title">Proposed classification</h2>
          <ClassificationCard
            verdict={(need.classification_verdict as 'single_resource' | 'it_service') || 'it_service'}
            confidence={need.classification_confidence || 0.93}
            rationale="Scope is a programme of 120 workloads over 18 months, not one named role. Result is deliverable based: landing zone, migration, cut-over support. No staff-augmentation framing; no individual role or named person requested."
            reviewThreshold={0.80}
          />
        </section>

        <section>
          <h2 className="classification-review-page__section-title">Decision rubric and exemplars used</h2>
          <DataTable
            rows={[
              { id: '1', verdict: 'single_resource', rubric: 'Individual role or staff augmentation', route: 'Vendor Management System (terminal)' },
              { id: '2', verdict: 'it_service', rubric: 'Outcome- or deliverable-based project or implementation service', route: 'Longlist flow (ATS5 onward)' },
            ] as RubricRow[]}
            headers={[
              { key: 'verdict', header: 'Verdict' },
              { key: 'rubric', header: 'Rubric' },
              { key: 'route', header: 'Route' },
            ]}
          >
            {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
              <Table {...getTableProps()} size="sm">
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
                        <TableCell key={cell.id}>
                          {cell.info.header === 'verdict' ? (
                            <Tag type={cell.value === 'single_resource' ? 'red' : 'blue'}>
                              {cell.value}
                            </Tag>
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

          <h3 className="classification-review-page__exemplar-heading">
            Exemplars referenced (audit trail)
          </h3>
          <ExemplarTable exemplars={exemplars} />
          <p className="classification-review-page__annotation">
            20 most recent human-confirmed exemplars are supplied to the classifier; 
            exemplars are refreshed weekly. The raw artifact is not shown to the classifier.
          </p>
        </section>
      </div>

      <section>
        <h2 className="classification-review-page__section-title">Reviewer decision</h2>
        <div className="classification-review-page__decision-grid">
          <div className="classification-review-page__card">
            <RadioButtonGroup
              name="review-decision"
              valueSelected={reviewDecision}
              onChange={(value) => setReviewDecision(value as 'approve' | 'modify' | 'reject')}
              orientation="vertical"
            >
              <RadioButton
                labelText="Approve proposed verdict: it_service"
                value="approve"
                id="approve"
              />
              <RadioButton
                labelText="Override to single_resource"
                value="modify"
                id="modify"
              />
              <RadioButton
                labelText="Request correction"
                value="reject"
                id="reject"
              />
            </RadioButtonGroup>

            <div className="classification-review-page__field">
              <TextArea
                id="rationale"
                labelText="Rationale (required, logged with the final decision)"
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                rows={4}
              />
            </div>

            {error && (
              <InlineNotification
                kind="error"
                title="Error"
                subtitle={error}
                lowContrast
              />
            )}

            <div className="classification-review-page__actions">
              <Button
                onClick={handleSubmit}
                disabled={submitting || !rationale}
                renderIcon={ArrowRight}
              >
                Confirm decision
              </Button>
              <Button kind="tertiary">
                Escalate to Procurement lead
              </Button>
            </div>
          </div>

          <div>
            <InlineNotification
              kind="warning"
              title="Low-confidence or borderline cases are held."
              subtitle="If the confidence falls below the threshold the case stays in the IT-service flow and waits in this queue. It is never auto-routed to VMS."
              lowContrast
            />
            <InlineNotification
              kind="info"
              title="SLA breach default."
              subtitle="If this review SLA is breached the case is held in the IT-service flow and escalated to the Procurement lead. Reclassification to single_resource must always be a reviewed action."
              lowContrast
            />

            <h3 className="classification-review-page__queue-heading">
              Other cases held in this queue
            </h3>
            <DataTable
              rows={[
                { id: 'NEED-2024-0417', need_id: 'NEED-2024-0417', proposed: 'single_resource', confidence: '0.74', state: 'held' },
                { id: 'NEED-2024-0409', need_id: 'NEED-2024-0409', proposed: 'it_service', confidence: '0.77', state: 'escalated' },
              ] as QueueRow[]}
              headers={[
                { key: 'need_id', header: 'need_id' },
                { key: 'proposed', header: 'Proposed' },
                { key: 'confidence', header: 'Confidence' },
                { key: 'state', header: 'State' },
              ]}
            >
              {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                <Table {...getTableProps()} size="sm">
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
                            className={cell.info.header === 'need_id' ? 'classification-review-page__mono' : ''}
                          >
                            {cell.info.header === 'state' ? (
                              <Tag type={cell.value === 'held' ? 'warm-gray' : 'red'}>
                                {cell.value === 'held' ? 'Held: low confidence' : 'SLA breached, escalated'}
                              </Tag>
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
          </div>
        </div>
      </section>
    </div>
  );
}
