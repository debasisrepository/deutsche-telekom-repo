import { InlineNotification, Tag } from '@carbon/react';
import { Longlist } from '../../types/governance';
import styles from './LockDetail.module.scss';

interface LockDetailProps {
  longlist: Longlist;
}

export function LockDetail({ longlist }: LockDetailProps) {
  return (
    <div className={styles.card}>
      <InlineNotification
        kind="success"
        title="Locked and immutable."
        subtitle="Supplier membership can no longer change. A change needs an explicit, controlled restart outside the normal flow."
        hideCloseButton
        className={styles.notification}
      />
      <dl className={styles.dl}>
        <dt>longlist_id</dt>
        <dd className={styles.mono}>{longlist.longlist_id}</dd>
        <dt>need_id</dt>
        <dd className={styles.mono}>{longlist.need_id}</dd>
        <dt>locked</dt>
        <dd>
          <Tag type="green">true</Tag> at{' '}
          <span className={styles.mono}>{longlist.locked_at}</span>
        </dd>
        <dt>Validation at lock</dt>
        <dd>
          <Tag type="green">{longlist.validation_verdict_at_lock || 'pass'}</Tag>{' '}
          {longlist.suppliers.length} suppliers (3 to 6)
        </dd>
        <dt>finalized_by</dt>
        <dd>{longlist.locked_by || 'Longlist Finalization Owner'}</dd>
        <dt>change_history</dt>
        <dd>{longlist.change_history.length} adjustments attached</dd>
      </dl>
    </div>
  );
}
