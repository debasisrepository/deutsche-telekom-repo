import { useState } from 'react';
import { TextInput, Button, InlineNotification } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import styles from './AdjustmentForm.module.scss';

interface AdjustmentFormProps {
  actor: string;
  onSubmit: (supplierId: string, action: 'add' | 'remove', reason: string) => Promise<void>;
}

export function AdjustmentForm({ actor, onSubmit }: AdjustmentFormProps) {
  const [supplierId, setSupplierId] = useState('');
  const [action, setAction] = useState<'add' | 'remove'>('add');
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(supplierId, action, reason);
      // Clear form on success
      setSupplierId('');
      setReason('');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Unknown error occurred');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.card}>
      <h3 className={styles.heading}>Record an adjustment</h3>
      <div className={styles.field}>
        <TextInput
          id="supplier-id"
          labelText="supplier_id"
          value={supplierId}
          onChange={(e) => setSupplierId(e.target.value)}
          invalid={error !== null}
          invalidText={error || ''}
        />
      </div>
      <div className={styles.field}>
        <TextInput
          id="action"
          labelText="action"
          value={action}
          onChange={(e) => setAction(e.target.value as 'add' | 'remove')}
          helperText="Allowed values: add, remove."
        />
      </div>
      <div className={styles.field}>
        <TextInput
          id="reason"
          labelText="reason (required)"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
      </div>
      <div className={styles.field}>
        <TextInput
          id="actor"
          labelText="actor"
          value={actor}
          readOnly
        />
      </div>
      <div className={styles.actions}>
        <Button
          onClick={handleSubmit}
          disabled={!supplierId || !action || !reason || isSubmitting}
          renderIcon={ArrowRight}
        >
          Record adjustment
        </Button>
      </div>
      <InlineNotification
        kind="info"
        title="Business-unit rights do not override the count gate, the lock gate or dispatch readiness."
        subtitle="Recording a change triggers a new ATS9 run."
        hideCloseButton
        className={styles.notification}
      />
    </div>
  );
}
