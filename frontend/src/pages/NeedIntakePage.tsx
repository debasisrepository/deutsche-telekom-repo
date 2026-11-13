import { useState, useEffect } from 'react';
import { InlineNotification, Tag, Grid, Column, Stack } from '@carbon/react';
import { NeedTable } from '../components/intake/NeedTable';
import { ChannelHealthTable } from '../components/intake/ChannelHealthTable';
import { NeedRecordDetail } from '../components/intake/NeedRecordDetail';
import { apiClient } from '../lib/api-client';
import type { Need, ChannelHealth } from '../types/need';
import './NeedIntakePage.scss';

export function NeedIntakePage() {
  const [needs, setNeeds] = useState<Need[]>([]);
  const [selectedNeed, setSelectedNeed] = useState<Need | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const channelHealth: ChannelHealth[] = [
    { channel: 'RFP document store', today: 9, rejected: 1 },
    { channel: 'E-mail inbox', today: 17, rejected: 1 },
    { channel: 'Phone-note capture (transcribed)', today: 8, rejected: 0 },
    { channel: 'Supplier offer inbox', today: 8, rejected: 1 },
  ];

  useEffect(() => {
    loadNeeds();
  }, []);

  const loadNeeds = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get<Need[]>('/intake/needs');
      const needsArray = Array.isArray(data) ? data : [];
      setNeeds(needsArray);
      if (needsArray.length > 0) {
        setSelectedNeed(needsArray[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load needs');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <p>Loading need intake data...</p>
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

  return (
    <div className="page-container">
      <Stack gap={5}>
        <p className="cds--label">Need queue / Intake / Normalization</p>
        <div className="page-header">
          <div>
            <h1 className="cds--productive-heading-06">
              Need Intake
            </h1>
            <p className="cds--body-01 page-lead">
              Every inbound submission from the four approved channels is converted into one normalized Need record before extraction starts.
            </p>
          </div>
          <Stack gap={3} className="page-tags">
            <Tag type="green">ATS1 - GREEN deterministic</Tag>
            <Tag type="gray">AGN1 / AGN5</Tag>
          </Stack>
        </div>

        <Grid narrow>
          <Column sm={4} md={2} lg={4}>
            <div className="intake-stat-tile">
              <span className="cds--label">Received today</span>
              <div className="intake-stat-big">42</div>
            </div>
          </Column>
          <Column sm={4} md={2} lg={4}>
            <div className="intake-stat-tile">
              <span className="cds--label">Normalized (status = normalized)</span>
              <div className="intake-stat-big">39</div>
            </div>
          </Column>
          <Column sm={4} md={2} lg={4}>
            <div className="intake-stat-tile">
              <span className="cds--label">Rejected (status = error)</span>
              <div className="intake-stat-big intake-stat-error">3</div>
            </div>
          </Column>
          <Column sm={4} md={2} lg={4}>
            <div className="intake-stat-tile">
              <span className="cds--label">Normalized within 5 minutes</span>
              <div className="intake-stat-big">100%</div>
            </div>
          </Column>
        </Grid>

        <InlineNotification
          kind="error"
          title="Rejected: NEED-2024-0412 (channel_type: email)."
          subtitle="Artifact body is empty after attachment parsing. The record was not passed to ATS2."
          lowContrast
        />

        <Grid narrow>
          <Column sm={4} md={5} lg={10}>
            <Stack gap={5}>
              <h2 className="cds--productive-heading-03">Inbound submissions</h2>
              <div className="intake-toolbar">
                <span>Filter by channel</span>
                <Stack gap={3} orientation="horizontal" className="intake-filter-tags">
                  <Tag type="outline">All channels</Tag>
                  <Tag type="blue">rfp</Tag>
                  <Tag type="blue">email</Tag>
                  <Tag type="blue">phone</Tag>
                  <Tag type="blue">supplier_offer</Tag>
                </Stack>
              </div>
              <NeedTable needs={needs} onRowClick={setSelectedNeed} selectedNeedId={selectedNeed?.id} />
              <p className="cds--helper-text-01">
                Showing {needs.length} needs. Channels are limited to rfp, email, phone and supplier_offer.
              </p>
            </Stack>
          </Column>

          <Column sm={4} md={3} lg={6}>
            <Stack gap={5}>
              <h2 className="cds--productive-heading-03">Channel health</h2>
              <ChannelHealthTable channels={channelHealth} />
              <InlineNotification
                kind="info"
                title=""
                subtitle="Event-driven ingestion, OAuth 2.0 service account per channel. Hard stop on schema-validation or audit-log write failure (BR-06)."
                lowContrast
                hideCloseButton
              />
            </Stack>
          </Column>
        </Grid>

        {selectedNeed && (
          <NeedRecordDetail
            need={selectedNeed}
            onOpenAttributeReview={() => {
              window.location.href = `/reviews/${selectedNeed.id}/attributes`;
            }}
            onViewAuditTrail={() => {
              console.log('View audit trail for', selectedNeed.id);
            }}
          />
        )}
      </Stack>
    </div>
  );
}
