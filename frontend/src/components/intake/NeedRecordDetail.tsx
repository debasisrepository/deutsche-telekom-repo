import { Button, TextArea, Tag, Grid, Column, Stack } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import type { Need } from '../../types/need';
import './NeedRecordDetail.scss';

interface NeedRecordDetailProps {
  need: Need;
  onOpenAttributeReview?: () => void;
  onViewAuditTrail?: () => void;
}

export function NeedRecordDetail({
  need,
  onOpenAttributeReview,
  onViewAuditTrail,
}: NeedRecordDetailProps) {
  const getStatusTagType = (status: string) => {
    if (status.startsWith('error')) return 'red';
    if (status === 'normalized') return 'green';
    return 'gray';
  };

  return (
    <Stack gap={5}>
      <h2 className="cds--productive-heading-03">
        Normalized Need record: {need.id}
      </h2>
      <Grid narrow>
        <Column sm={4} md={4} lg={8}>
          <div className="need-record-card">
            <h3 className="cds--productive-heading-02 need-record-heading">
              Authoritative record (DPS1)
            </h3>
            <dl className="need-record-dl">
              <dt className="cds--label">need_id</dt>
              <dd className="cds--type-mono need-record-dd">
                {need.id}
              </dd>
              <dt className="cds--label">business_unit_id</dt>
              <dd className="cds--type-mono need-record-dd">
                {need.business_unit_id}
              </dd>
              <dt className="cds--label">channel_type</dt>
              <dd className="cds--type-mono need-record-dd">
                {need.channel_type}
              </dd>
              <dt className="cds--label">arrival_timestamp</dt>
              <dd className="cds--type-mono need-record-dd">
                {need.arrival_timestamp}
              </dd>
              <dt className="cds--label">raw_artifact_ref</dt>
              <dd className="need-record-dd">
                <a href="#" className="cds--link cds--type-mono">
                  {need.raw_artifact_ref}
                </a>
              </dd>
              <dt className="cds--label">status</dt>
              <dd className="need-record-dd">
                <Tag type={getStatusTagType(need.status)}>{need.status}</Tag>
              </dd>
              <dt className="cds--label">pii_masked</dt>
              <dd className="need-record-dd">
                <Tag type="purple">true</Tag>
              </dd>
            </dl>
            <Stack gap={5} className="need-record-actions">
              {onOpenAttributeReview && (
                <Button onClick={onOpenAttributeReview} renderIcon={ArrowRight}>
                  Open attribute review (ATS2)
                </Button>
              )}
              {onViewAuditTrail && (
                <Button kind="tertiary" onClick={onViewAuditTrail}>
                  View audit trail
                </Button>
              )}
            </Stack>
          </div>
        </Column>
        <Column sm={4} md={4} lg={8}>
          <div className="need-record-card">
            <h3 className="cds--productive-heading-02 need-record-heading">
              PII stripped or masked before hand-off
            </h3>
            <Stack gap={5}>
              <div>
                <label htmlFor="raw" className="cds--label need-record-label">
                  Raw submission excerpt (read-only, reviewer access)
                </label>
                <TextArea
                  id="raw"
                  labelText=""
                  readOnly
                  value="Contact person details removed. Request for managed migration of 120 workloads to sovereign cloud in 2025."
                  rows={3}
                />
              </div>
              <div>
                <label htmlFor="norm" className="cds--label need-record-label">
                  Normalized free text passed downstream
                </label>
                <TextArea
                  id="norm"
                  labelText=""
                  readOnly
                  value="Contact [NAME MASKED] ([EMAIL MASKED], [PHONE MASKED]) for managed migration of 120 workloads to sovereign cloud in 2025."
                  rows={3}
                />
              </div>
              <p className="cds--helper-text-01">
                All channels produce one common record structure. The normalized record is the only
                object handed to ATS2.
              </p>
            </Stack>
          </div>
        </Column>
      </Grid>
    </Stack>
  );
}
