import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Button, TextArea, InlineNotification, Tag, Grid, Column, Stack } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import { AttributeTable } from '../components/review/AttributeTable';
import { SourceComparison } from '../components/review/SourceComparison';
import { apiClient } from '../lib/api-client';
import type { Need } from '../types/need';
import type { NeedAttribute, AttributeReviewRequest } from '../types/review';
import './AttributeReviewPage.scss';

export function AttributeReviewPage() {
  const { needId } = useParams<{ needId: string }>();
  const [need, setNeed] = useState<Need | null>(null);
  const [attributes, setAttributes] = useState<NeedAttribute[]>([]);
  const [reviewerNotes, setReviewerNotes] = useState('Budget in source is non-numeric; corrected to source wording. Added second delivery location.');
  const [budgetCorrection, setBudgetCorrection] = useState('To be agreed with business unit');
  const [locationCorrection] = useState('Bonn and Darmstadt, Germany');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (needId) {
      loadNeedData(needId);
    }
  }, [needId]);

  const loadNeedData = async (id: string) => {
    try {
      setLoading(true);
      const needData = await apiClient.get<Need>(`/intake/needs/${id}`);
      setNeed(needData);

      const mockAttributes: NeedAttribute[] = [
        { field: 'service_type', value: 'Managed cloud migration service', confidence: 0.94, action: 'keep' },
        { field: 'scope_description', value: 'Migration and 24x7 operation of 120 on-premise workloads to a sovereign cloud, incl. landing zone, data migration and cut-over support', confidence: 0.91, action: 'keep' },
        { field: 'estimated_volume_duration', value: '120 workloads, 18 months', confidence: 0.88, action: 'keep' },
        { field: 'required_skills', value: 'Cloud architecture, Kubernetes, data migration, ISO 27001', confidence: 0.86, action: 'keep' },
        { field: 'budget_indication', value: 'EUR 2.0 - 2.5 million (inferred)', confidence: 0.58, action: 'modify' },
        { field: 'delivery_location', value: 'Bonn, Germany', confidence: 0.71, action: 'modify' },
      ];
      setAttributes(mockAttributes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load need data');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!needId) return;
    
    try {
      const request: AttributeReviewRequest = {
        review_decision: 'approve',
        need_attributes: {
          budget_indication: budgetCorrection,
          delivery_location: locationCorrection,
        },
        reviewer_notes: reviewerNotes,
      };
      
      await apiClient.post(`/reviews/needs/${needId}/attributes`, request);
      alert('Attributes approved and advancing to ATS3');
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to approve'}`);
    }
  };

  const handleSaveModifications = async () => {
    if (!needId) return;
    
    try {
      const request: AttributeReviewRequest = {
        review_decision: 'modify',
        need_attributes: {
          budget_indication: budgetCorrection,
          delivery_location: locationCorrection,
        },
        reviewer_notes: reviewerNotes,
      };
      
      await apiClient.post(`/reviews/needs/${needId}/attributes`, request);
      alert('Modifications saved');
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to save'}`);
    }
  };

  const handleReject = async () => {
    if (!needId) return;
    
    try {
      const request: AttributeReviewRequest = {
        review_decision: 'reject',
        reviewer_notes: reviewerNotes,
      };
      
      await apiClient.post(`/reviews/needs/${needId}/attributes`, request);
      alert('Extraction rejected, returning for remediation');
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to reject'}`);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <p>Loading attribute review data...</p>
      </div>
    );
  }

  if (error || !need) {
    return (
      <div className="page-container">
        <InlineNotification
          kind="error"
          title="Error loading data"
          subtitle={error || 'Need not found'}
          lowContrast
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      <Stack gap={5}>
        <p className="cds--label">Review workbench / {need.id} / ATS2 attribute review</p>
        <div className="page-header">
          <div>
            <h1 className="cds--productive-heading-06">
              Attribute Review: Extracted need attributes
            </h1>
            <p className="cds--body-01 page-lead">
              AGN1 proposes a structured attribute set with per-field confidence. The reviewer compares each value with the raw artifact and approves, modifies or rejects.
            </p>
          </div>
          <Stack gap={3} className="page-tags">
            <Tag type="warm-gray">ATS2 - AMBER human review</Tag>
            <Tag type="gray">AGN1</Tag>
            <Tag type="gray">Review status: extraction_review_pending</Tag>
          </Stack>
        </div>

        <div className="review-casebar">
          <div><span className="cds--label">need_id</span><span className="cds--type-mono">{need.id}</span></div>
          <div><span className="cds--label">business_unit_id</span>{need.business_unit_id}</div>
          <div><span className="cds--label">channel_type</span>{need.channel_type}</div>
          <div><span className="cds--label">raw_artifact_ref</span><a href="#" className="cds--link cds--type-mono">{need.raw_artifact_ref}</a></div>
          <div><span className="cds--label">Next step</span><a href={`/reviews/${need.id}/classification`} className="cds--link">ATS3 Classification review</a></div>
        </div>

        <InlineNotification
          kind="warning"
          title="2 fields need attention."
          subtitle="budget_indication (confidence 0.58) and delivery_location (confidence 0.71) are below the review threshold."
          lowContrast
        />

        <Grid narrow>
          <Column sm={4} md={5} lg={10}>
            <Stack gap={5}>
              <h2 className="cds--productive-heading-03">NeedAttributes</h2>
              <AttributeTable attributes={attributes} />
              <p className="cds--helper-text-01">
                Schema validation: all 7 required keys present. Outputs failing schema validation are held for remediation.
              </p>
            </Stack>
          </Column>

          <Column sm={4} md={3} lg={6}>
            <SourceComparison
              rawExcerpt={`"...the budget for the migration programme is to be agreed with the business unit; last year's comparable project was in the low single-digit millions. Service will be delivered for our Bonn and Darmstadt data centres..."`}
              fieldName="budget_indication"
              fieldValue={budgetCorrection}
              onFieldChange={setBudgetCorrection}
            />
          </Column>
        </Grid>

        <Stack gap={5}>
          <h2 className="cds--productive-heading-03">Reviewer decision</h2>
          <Grid narrow>
            <Column sm={4} md={4} lg={8}>
              <div className="review-decision-card">
                <Stack gap={5}>
                  <div>
                    <label htmlFor="notes" className="cds--label review-label">
                      Reviewer notes (logged against the need record)
                    </label>
                    <TextArea
                      id="notes"
                      labelText=""
                      value={reviewerNotes}
                      onChange={(e) => setReviewerNotes(e.target.value)}
                      rows={3}
                    />
                  </div>
                  <Stack gap={5} orientation="horizontal" className="review-actions">
                    <Button onClick={handleApprove} renderIcon={ArrowRight}>
                      Approve and continue to ATS3
                    </Button>
                    <Button kind="secondary" onClick={handleSaveModifications}>
                      Save modifications
                    </Button>
                    <Button kind="danger" onClick={handleReject}>
                      Reject extraction
                    </Button>
                  </Stack>
                </Stack>
              </div>
            </Column>
            <Column sm={4} md={4} lg={8}>
              <div className="review-decision-card">
                <Stack gap={5}>
                  <h3 className="cds--productive-heading-02">What is logged</h3>
                  <p className="cds--body-01">
                    Full extracted attribute set, field-level confidence, model and prompt version, reviewer identity, each correction (field, old value, new value) and the final decision, retained 7 years.
                  </p>
                  <InlineNotification
                    kind="info"
                    title=""
                    subtitle="Approve and modify both release the case to ATS3 (classification_review_pending). Reject returns it for extraction remediation."
                    lowContrast
                    hideCloseButton
                  />
                </Stack>
              </div>
            </Column>
          </Grid>
        </Stack>
      </Stack>
    </div>
  );
}
