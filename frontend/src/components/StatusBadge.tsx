const STATUS_STYLES: Record<string, string> = {
  uploaded: 'bg-ink text-white',
  needs_review: 'bg-citrus text-ink',
  validated: 'bg-mint text-ink',
  rejected: 'bg-red-500 text-white',
}

export default function StatusBadge({ status }: { status: string }){
  const cls = STATUS_STYLES[status] || 'bg-gray-200 text-ink'
  return <span className={`badge ${cls}`}>{status}</span>
}
