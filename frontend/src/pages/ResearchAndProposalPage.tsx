import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Stack, Grid, Column, Tag, InlineNotification, Button, TextArea } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import { NicheCandidateTable } from '../components/proposal/NicheCandidateTable';
import { RankedSupplierTable } from '../components/proposal/RankedSupplierTable';
import { CitationBadge } from '../components/proposal/CitationBadge';
import { apiClient } from '../lib/api-client';
import type { NicheResearchResponse, LonglistProposalResponse } from '../types/proposal';
import './ResearchAndProposalPage.scss';

export function ResearchAndProposalPage() {
  const { needId } = useParams<{ needId: string }>();
  const [researchData, setResearchData] = useState<NicheResearchResponse | null>(null);
  const [proposalData, setProposalData] = useState<LonglistProposalResponse | null>(null);
  const [reviewerNote, setReviewerNote] = useState('Accept ranking. Keep SUP-0518 pending scope confirmation.');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!needId) return;

    try {
      setLoading(true);
      setError(null);

      // Load niche research data
      try {
        const researchResponse = await apiClient.post<NicheResearchResponse>('/niche-research', {
          need_id: needId,
          capability_gap: 'Sovereign-cloud data classification for OT workloads',
          approved_source_list: ['Gaia-X register', 'BSI C5 list', 'industry association directories'],
        });
        setResearchData(researchResponse);
      } catch (err) {
        console.warn('Niche research not available:', err);
      }

      // Load proposal data
      const proposalResponse = await apiClient.post<LonglistProposalResponse>('/longlist-proposals', {
        need_id: needId,
        matched_panels: [],
        evidence_items: [],
        approved_niche_candidates: [],
      });
      setProposalData(proposalResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load research and proposal data');
    } finally {
      setLoading(false);
    }
  }, [needId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAcceptProposal = () => {
    console.log('Accept proposal for', needId);
  };

  const handleModifyProposal = () => {
    console.log('Modify proposal for', needId);
  };

  const handleRejectProposal = () => {
    console.log('Reject proposal for', needId);
  };

  if (loading) {
    return (
      <div className="page-container">
        <p>Loading research and proposal data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <InlineNotification
          kind="error"
          title="Error loading data"
          subtitle={error}
          lowContrast
        />
      </div>
    );
  }

  if (!proposalData) {
    return (
      <div className="page-container">
        <p>No proposal data available</p>
      </div>
    );
  }

  const citationCoverage = 100;

  return (
    <div className="page-container">
      <Stack gap={5}>
        <p className="cds--label">Review workbench / {needId} / Niche research and ranked longlist</p>

        <div className="page-header">
          <div>
            <h1 className="cds--productive-heading-06">
              Niche provider research and ranked longlist proposal
            </h1>
            <p className="cds--body-01 page-lead">
              Researched providers and the ranked proposal are recommendations. Nothing becomes eligible, 
              or moves to finalization, until a reviewer accepts, modifies or rejects it. 
              Every supplier carries a citation or is rejected.
            </p>
          </div>
          <Stack gap={3} className="page-tags">
            <Tag type="warm-gray">ATS7 - AMBER</Tag>
            <Tag type="warm-gray">ATS8 - AMBER</Tag>
            <Tag type="gray">AGN2</Tag>
          </Stack>
        </div>

        {researchData && researchData.niche_research_dossier.length > 0 && (
          <section>
            <h2 className="cds--productive-heading-04">
              ATS7 Niche-provider research dossier
            </h2>

            <Grid narrow>
              <Column sm={4} md={8} lg={10}>
                <NicheCandidateTable candidates={researchData.niche_research_dossier} />
                <div className="research-actions">
                  <Button renderIcon={ArrowRight} iconDescription="Confirm">
                    Confirm accepted candidates
                  </Button>
                  <Button kind="tertiary">
                    Reject all candidates
                  </Button>
                </div>
              </Column>
              <Column sm={4} md={8} lg={6}>
                <div className="research-basis-card">
                  <h3 className="cds--productive-heading-02">Research basis</h3>
                  <dl className="research-basis-dl">
                    <dt>Capability gap</dt>
                    <dd>Sovereign-cloud data classification for OT workloads</dd>
                    <dt>Approved sources</dt>
                    <dd>Gaia-X register, BSI C5 list, industry association directories</dd>
                    <dt>Source freshness</dt>
                    <dd>No older than 30 days at retrieval</dd>
                    <dt>Panel matches passed</dt>
                    <dd>3 of 5 (SUP-0231, SUP-0118, SUP-0045)</dd>
                  </dl>
                  <InlineNotification
                    kind="error"
                    title="Halt rule."
                    subtitle="If no governed sources can be retrieved, this step stops and surfaces the gap. Providers are never invented."
                    lowContrast
                    hideCloseButton
                  />
                </div>
              </Column>
            </Grid>
          </section>
        )}

        <section>
          <h2 className="cds--productive-heading-04">
            ATS8 Ranked longlist proposal
          </h2>

          <div className="proposal-casebar">
            <div>
              <span className="cds--label">proposal_id</span>
              <span className="cds--body-01 mono">{proposalData.proposal_id}</span>
            </div>
            <div>
              <span className="cds--label">need_id</span>
              <span className="cds--body-01 mono">{needId}</span>
            </div>
            <div>
              <span className="cds--label">evidence_limited_flag</span>
              <Tag type={proposalData.evidence_limited_flag ? 'warm-gray' : 'green'}>
                {proposalData.evidence_limited_flag ? 'true' : 'false'}
              </Tag>
            </div>
            <div>
              <span className="cds--label">Suppliers proposed</span>
              <span className="cds--body-01">
                {proposalData.ranked_suppliers.length} (target band 3 to 6)
              </span>
            </div>
            <div>
              <CitationBadge citationCoverage={citationCoverage} required={98} />
            </div>
          </div>

          <RankedSupplierTable suppliers={proposalData.ranked_suppliers} />

          {proposalData.evidence_limited_flag && (
            <InlineNotification
              kind="warning"
              title="Evidence limited."
              subtitle="Evidence came from the representative data set. Reviewers should weigh rankings 3 to 5 accordingly. A proposal containing an uncited supplier is rejected automatically."
              lowContrast
            />
          )}

          <Grid narrow className="proposal-decision">
            <Column sm={4} md={4} lg={8}>
              <div className="proposal-decision-card">
                <div className="proposal-decision-field">
                  <TextArea
                    id="reviewer-note"
                    labelText="Reviewer note"
                    value={reviewerNote}
                    onChange={(e) => setReviewerNote(e.target.value)}
                    rows={3}
                  />
                </div>
                <div className="proposal-decision-actions">
                  <Button
                    onClick={handleAcceptProposal}
                    renderIcon={ArrowRight}
                    iconDescription="Accept"
                  >
                    Accept proposal and continue
                  </Button>
                  <Button kind="secondary" onClick={handleModifyProposal}>
                    Modify
                  </Button>
                  <Button kind="danger" onClick={handleRejectProposal}>
                    Reject
                  </Button>
                </div>
              </div>
            </Column>
            <Column sm={4} md={4} lg={8}>
              <div className="proposal-gate-rules">
                <h3 className="cds--productive-heading-02">Gate rules</h3>
                <ul>
                  <li>The proposal stays a recommendation until review is complete.</li>
                  <li>No fabricated supplier names; no uncited ranking.</li>
                  <li>Supplier count (3 to 6) is enforced deterministically in the next step (ATS9).</li>
                </ul>
              </div>
            </Column>
          </Grid>
        </section>
      </Stack>
    </div>
  );
}
