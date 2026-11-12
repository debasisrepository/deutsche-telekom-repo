export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function formatCurrency(amount: number, currency = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount)
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('de-DE')
}

export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function getStatusBadgeColor(status: string): string {
  const statusColorMap: Record<string, string> = {
    intake_pending: 'bg-gray-200 text-gray-800',
    intake_normalized: 'bg-blue-200 text-blue-800',
    extraction_pending: 'bg-yellow-200 text-yellow-800',
    classification_pending: 'bg-orange-200 text-orange-800',
    vms_routed: 'bg-purple-200 text-purple-800',
    evidence_retrieval: 'bg-indigo-200 text-indigo-800',
    longlist_proposed: 'bg-teal-200 text-teal-800',
    validation_pending: 'bg-amber-200 text-amber-800',
    locked: 'bg-green-200 text-green-800',
    dispatched: 'bg-green-600 text-white',
  }
  return statusColorMap[status] || 'bg-gray-200 text-gray-800'
}
