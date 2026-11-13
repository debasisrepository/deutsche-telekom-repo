import { Tag } from '@carbon/react';

interface DispatchStatusBadgeProps {
  status: 'pending' | 'delivered' | 'retrying' | 'failed' | 'escalated';
}

export function DispatchStatusBadge({ status }: DispatchStatusBadgeProps) {
  const getTagType = () => {
    switch (status) {
      case 'delivered':
        return 'green';
      case 'retrying':
        return 'cyan';
      case 'escalated':
      case 'failed':
        return 'red';
      case 'pending':
      default:
        return 'gray';
    }
  };

  return <Tag type={getTagType()}>{status}</Tag>;
}
