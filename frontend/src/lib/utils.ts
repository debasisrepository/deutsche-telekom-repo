import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount);
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('de-DE');
}

export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function getStatusBadgeColor(status: string): string {
  const statusColors: Record<string, string> = {
    pending: 'gray',
    classified_it_service: 'blue',
    vms_routed_terminal: 'green',
    evidence_retrieved: 'cyan',
    proposal_reviewed: 'purple',
  };
  return statusColors[status] || 'gray';
}
