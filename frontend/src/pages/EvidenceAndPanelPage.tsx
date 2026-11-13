import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Stack, Grid, Column, Tag, InlineNotification } from '@carbon/react';
import { EvidenceTable } from '../components/evidence/EvidenceTable';
import { PanelMatchTable } from '../components/evidence/PanelMatchTable';
import { CoverageGapCard } from '../components/evidence/CoverageGapCard';
import { apiClient } from '../lib/api-client';
import type { EvidenceQueryResponse, PanelMappingResponse } from '../types/evidence';
import './EvidenceAndPanelPage.scss';

export function EvidenceAndPanelPage() {
  const { needId } = useParams<{ needId: string }>();
  const navigate = useNavigate();
  const [evidenceData, setEvidenceData] = useState<EvidenceQueryResponse | null>(null);
  const [panelData, setPanelData] = useState<PanelMappingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!needId) return;

    try {
      setLoading(true);
      setError(null);

      // Load evidence data
      const evidenceResponse = await apiClient.post<EvidenceQueryResponse>('/evidence/queries', {
        need_id: needId,
      });
      setEvidenceData(evidenceResponse);

      // Load panel mapping data
      const panelResponse = await apiClient.post<PanelMappingResponse>('/panel-mappings', {
        need_id: needId,
        need_category: 'Cloud migration',
      });
      setPanelData(panelResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load evidence and panel data');
    } finally {
      setLoading(false);
    }
  }, [needId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStartNicheResearch = () => {
    if (needId) {
      navigate(`/research/${needId}`);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <p>Loading evidence and panel mapping data...</p>
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

  if (!evidenceData || !panelData) {
    return (
      <div className="page-container">
        <p>No data available</p>
      </div>
    );
  }

  const evidenceItems = evidenceData.evidence_items || [];
  const suppliersWithEvidence = new Set(evidenceItems.map(item => item.supplier_id)).size;
  const snapshotDate = new Date(evidenceData.evidence_snapshot_timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  });

  return (
    <div className="page-container">
      <Stack gap={5}>
        <p className="cds--label">Review workbench / {needId} / Evidence and panel mapping</p>

        <div className="page-header">
          <div>
            <h1 className="cds--productive-heading-06">
              Historical evidence and panel mapping
            </h1>
            <p className="cds--body-01 page-lead">
              For a reviewed IT-service need, the rule engine retrieves cited supplier and project evidence 
              and maps the need to pre-selection panels and functional groups. Nothing here is invented: 
              missing data is flagged, not filled.
            </p>
          </div>
          <Stack gap={3} className="page-tags">
            <Tag type="green">ATS5 - GREEN</Tag>
            <Tag type="green">ATS6 - GREEN</Tag>
            <Tag type="gray">AGN2 / AGN5</Tag>
            <Tag type="gray">TOL2 / TOL3</Tag>
          </Stack>
        </div>

        <div className="evidence-casebar">
          <div>
            <span className="cds--label">need_id</span>
            <span className="cds--body-01 mono">{needId}</span>
          </div>
          <div>
            <span className="cds--label">service_type</span>
            <span className="cds--body-01">Managed cloud migration service</span>
          </div>
          <div>
            <span className="cds--label">need_category</span>
            <span className="cds--body-01">Cloud migration</span>
          </div>
          <div>
            <span className="cds--label">Verdict</span>
            <Tag type="blue">it_service (reviewed)</Tag>
          </div>
        </div>

        <section>
          <h2 className="cds--productive-heading-04">
            ATS5 Historical supplier and project evidence
          </h2>
          
          <Grid narrow className="evidence-metrics">
            <Column sm={4} md={8} lg={4}>
              <div className="evidence-metric-tile">
                <span className="cds--label">Evidence items retrieved</span>
                <div className="evidence-metric-big">{evidenceItems.length}</div>
              </div>
            </Column>
            <Column sm={4} md={8} lg={4}>
              <div className="evidence-metric-tile">
                <span className="cds--label">Suppliers with evidence</span>
                <div className="evidence-metric-big">{suppliersWithEvidence}</div>
              </div>
            </Column>
            <Column sm={4} md={8} lg={4}>
              <div className="evidence-metric-tile">
                <span className="cds--label">evidence_snapshot_timestamp</span>
                <div className="evidence-metric-timestamp">{snapshotDate}</div>
                <div className="cds--helper-text-01">Nightly load (T-1)</div>
              </div>
            </Column>
          </Grid>

          {evidenceData.evidence_limited_flag && (
            <InlineNotification
              kind="warning"
              title="evidence_limited_flag = true."
              subtitle="The live historical order and commissioned-SoW repository is not yet available. Results come from the governed representative data set and are labelled as such. Rankings must carry only citations that exist in this set."
              lowContrast
            />
          )}

          <div className="evidence-toolbar">
            <span>Filter: panel <Tag type="outline">Cloud and hosting</Tag> functional group <Tag type="outline">Migration services</Tag></span>
            <Tag type="purple">Representative governed data</Tag>
          </div>

          <EvidenceTable items={evidenceItems} />

          <p className="cds--helper-text-01">
            Showing {evidenceItems.length} items. Empty or unavailable source: the step continues in approved fallback 
            (panel mapping only), sets evidence_limited_flag and never fabricates supplier history, SoWs or supplier names.
          </p>
        </section>

        <section>
          <h2 className="cds--productive-heading-04">
            ATS6 Pre-selection panels and functional groups
          </h2>

          <Grid narrow>
            <Column sm={4} md={8} lg={10}>
              <PanelMatchTable candidates={panelData.candidate_suppliers} />
              <p className="cds--helper-text-01">
                Every candidate shows panel or functional-group provenance, so a later ranking can always be traced to its basis. 
                {panelData.candidate_suppliers.length} candidates mapped.
              </p>
            </Column>
            <Column sm={4} md={8} lg={6}>
              <CoverageGapCard
                coverageGapFlag={panelData.coverage_gap_flag}
                onStartNicheResearch={handleStartNicheResearch}
              />
            </Column>
          </Grid>
        </section>
      </Stack>
    </div>
  );
}
